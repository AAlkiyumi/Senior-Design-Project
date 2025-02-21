import random
from scrapingbee import ScrapingBeeClient
import time
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import pandas as pd
import re
import inspect

import amazon1
import api_keys

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()



CONCURRENCY = 80

def get_reviews_worker(n, q):
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                print("Getting json...")
                x = get_reviews(data)
                print("Got json!")

                # put the reviews into the global variable review_result where each thread will have a designated index
                # where it can safely append new revuews
                global review_dictionary_list
                for my_dict in x:
                    review_dictionary_list[n] += [my_dict]
                print("Great Success")
                q.task_done()
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                
                print("Couldn't get data from", data)
                q.task_done()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            print("Thread", n, "has joined")
            break

def get_reviews(product_dictionary, retries=0):
    MAX_RETRIES = 10
    if retries > MAX_RETRIES:
        return
    
    if product_dictionary["sku"] == "":
        try:
            asin = product_dictionary["url"].split("/dp/")[1].split("/")[0]
            product_dictionary["sku"] = asin
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            asin = ""
    else:
        asin = product_dictionary["sku"]
    
    #if we have the asin and not the model nummber we can plud it in
    if (product_dictionary["Model No."] == "") and (asin != ""):
        product_dictionary["Model No."] = "ASIN: " + asin
    
    #if we don't have the asin the url wont work
    if asin == "":
        return []

    review_url = "https://www.amazon.com/product-reviews/" + asin + "/ref=cm_cr_arp_d_viewopt_fmt?ie=UTF8&reviewerType=all_reviews&pageNumber=" + str(product_dictionary["page_number"]) +"&sortBy=recent&formatType=current_format"
    product_dictionary["url"] = review_url
    print(review_url)
    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    try:
        response = client.get(
            review_url,
            params={
                #"render_js": False,
                "block_resources": False,
                "premium_proxy": True,
                "country_code": "us"
            },
            timeout=30
        )
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        print("Couldn't get reviews for", product_dictionary)
        return get_reviews(product_dictionary, retries+1)

    print(response.status_code)
    print(response.content)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return parse_soup(soup, product_dictionary)
    elif response.status_code == 429:
        print("Too many requests, sleeping for 5 seconds")
        time.sleep(5)
        return get_reviews(product_dictionary, retries)

    elif (response.status_code != 200):
        return get_reviews(product_dictionary, retries+1)
       
    else:
        print("Couldn't get reviews for", product_dictionary)

def parse_soup(soup, product_dictionary):
    
    if product_dictionary["Manufacturer"] == "":
        try:
            product_dictionary["Manufacturer"] = soup.find("div", {"data-hook": "cr-product-byline"}).find("a", {"class": "a-size-base a-link-normal"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            product_dictionary["Manufacturer"] = ""

    review_list = []
    review_cards = soup.find_all("div", {"data-hook": "review"})
    for review in review_cards:
        print(review)
        try: # dont really need this particular try/except block but it's here
            try:
                title_soup = review.find("a", {"data-hook": "review-title"}).find_all("span")
                review_title = title_soup[-1].text.strip()
                
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                review_title = ''

            
            try:
                star_rating_soup = review.find("i", {"data-hook": "review-star-rating"})
                star_rating = int(star_rating_soup.text.strip()[0])
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                star_rating = ''

            
            try:
                review_date_soup = review.find("span", {"data-hook": "review-date"})
                date_string = " ".join(review_date_soup.text.strip().split(' ')[-3:])
                date_format = "%B %d, %Y"
                review_date = datetime.strptime(date_string, date_format)
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                review_date = ''

            
            try:
                review_text = review.find("span", {"data-hook": "review-body"}).text.strip()

            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                review_text = ''
            
            try:
                review_author = review.find("span", {"class": "a-profile-name"}).text.strip()
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                review_author = ''
            
            try:
                location = review.find("span", {"data-hook": "review-date"}).text.strip().split("Reviewed in the ")[1].split(" on")[0]
                location = location.strip()

            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                location = ''
            
            try:
                verified_purchase_badge = soup.find("span", {"data-hook": "avp-badge"}).text.strip()
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                verified_purchase_badge = ''
            try:
                image_list = []
                image_section = review.find("div", {"class": "a-section a-spacing-medium review-image-container"})
                image_segments = image_section.find_all("img", {"class": "review-image-tile"})
                for image in image_segments:
                    image_list += [image["src"]]
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                image_list = []
            
            review_dictionary = {
                "Type": product_dictionary["Type"],
                "Store": product_dictionary["Store"],
                "Manufacturer": product_dictionary["Manufacturer"],
                "Model No.": product_dictionary["Model No."],
                "Price": product_dictionary["Price"],
                "Model Description": product_dictionary["Model Description"],
                "sku": product_dictionary["sku"],
                "url": product_dictionary["url"],
                "product_image": product_dictionary["product_image"],
                "star_rating": star_rating,
                "review_title": review_title,
                "review_text": review_text,
                "review_date": review_date,
                "review_author": review_author,
                "original_review_syndication": "", #not available on amazon that I know of
                "location": location, # extra will be dropped from returned df
                "recommended": "", # not available on amazon
                "verified_purchase_badge": verified_purchase_badge,
                "image_list": image_list
            }
            review_list += [review_dictionary]
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            print("Couldn't parse review")

    check_if_need_next_page(product_dictionary, review_list)
    return review_list

def check_if_need_next_page(product_dictionary, review_list):
    # find the oldest date from review list
    # iterate through review list and put dates into a list
    review_date_list = []
    for review_dictionary in review_list:
        review_date_list += [review_dictionary["review_date"]]
    
    minimum_date = min(review_date_list)
    global n_days_ago_global
    if (minimum_date > n_days_ago_global) and (len(review_list) >= 10):
        if product_dictionary["page_number"] < 100:
            product_dictionary["page_number"] += 1
            product_dictionary_q.put(product_dictionary)
        else:
            print("Already went back 100 pages, stopping")





def days_back(n_days):
    # input: integer n_days (number of days to go back)
    # output: datetime n_days_ago (round to the start of the day)
    todays_date = datetime.now()
    n_days_ago = (todays_date - timedelta(days=n_days)).replace(hour=0, minute=0, second=0, microsecond=0)
    print("Scraping reviews going back until", n_days_ago)
    return n_days_ago


    


        
        


product_dictionary_q = Queue(maxsize=0)
review_dictionary_list = [[] for i in range(CONCURRENCY)]
n_days_ago_global = ""

def main(start_url_list, appliance_type, number_of_pages, guaranteed_product_hrefs, n_days_ago):
    
    global product_dictionary_q
    product_dictionary_q = Queue(maxsize=0)

    global review_dictionary_list
    review_dictionary_list = [[] for i in range(CONCURRENCY)]

    global n_days_ago_global
    n_days_ago_global = n_days_ago

    starting_dataframe = amazon1.main(start_url_list, appliance_type, number_of_pages, guaranteed_product_hrefs)

    for index, row in starting_dataframe.iterrows():
        product_dictionary_q.put(row.to_dict())

    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_reviews_worker, args=(i, product_dictionary_q))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    dataframe_to_export = pd.DataFrame()
    for my_list in review_dictionary_list:
        #convery list of dictionaries to pandas dataframe
        
        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)

        dataframe_to_export = dataframe_to_export._append(pd.DataFrame(my_list), ignore_index=True)
    
    
    dataframe_to_export.to_excel("outputs/Reviews/" + "Amazon.com " + appliance_type + " Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    
    # drop location column 
    try:
        dataframe_to_export = dataframe_to_export.drop(columns=["location"], axis=1)
    except Exception as e:
        print(e)
    
    return dataframe_to_export

if __name__ == "__main__":
    
    """
    mandatory_dehum_href_list = [
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B08ZMY8BC8/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B07NRC42PJ/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B09155CW3S/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B09155CW3S/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B091BYVD2W/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B0915DV55B/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B0866XLRTX/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1"
    ]

    mandatory_wac_href_list = [
        "https://www.amazon.com/Midea-Inverter-Conditioner-Flexibility-Installation/dp/B08677DCKN/ref=sr_1_1?crid=2MSH5ND0XPV1B&keywords=MAW08V1QWT&qid=1677255497&s=home-garden&sprefix=maw08v1qwt%2Cgarden%2C77&sr=1-1",
        "https://www.amazon.com/Midea-Inverter-Conditioner-Flexibility-Installation/dp/B0866Y33PL/ref=sr_1_1?crid=2MSH5ND0XPV1B&keywords=MAW08V1QWT&qid=1677255497&s=home-garden&sprefix=maw08v1qwt%2Cgarden%2C77&sr=1-1&th=1",
        "https://www.amazon.com/Midea-Inverter-Conditioner-Flexibility-Installation/dp/B0867GMW9X/ref=sr_1_1?crid=2MSH5ND0XPV1B&keywords=MAW08V1QWT&qid=1677255497&s=home-garden&sprefix=maw08v1qwt%2Cgarden%2C77&sr=1-1&th=1",
        "https://www.amazon.com/Midea-EasyCool-Conditioner-Fan-Cools-Mechanical/dp/B085797ZFF/ref=sr_1_2?crid=1ISHR9ND9AYXA&keywords=MAW05M1BWT&qid=1677255565&s=home-garden&sprefix=maw05m1bwt%2Cgarden%2C76&sr=1-2&th=1",
        "https://www.amazon.com/Midea-EasyCool-Conditioner-Fan-Cools-Mechanical/dp/B07PDXKDZH/ref=sr_1_2?crid=1ISHR9ND9AYXA&keywords=MAW05M1BWT&qid=1677255565&s=home-garden&sprefix=maw05m1bwt%2Cgarden%2C76&sr=1-2&th=1",
        "https://www.amazon.com/Midea-EasyCool-Conditioner-Fan-Cools-Mechanical/dp/B07PDXKSGJ/ref=sr_1_2?crid=1ISHR9ND9AYXA&keywords=MAW05M1BWT&qid=1677255565&s=home-garden&sprefix=maw05m1bwt%2Cgarden%2C76&sr=1-2&th=1",
        "https://www.amazon.com/Midea-EasyCool-Conditioner-Fan-Cools-Mechanical/dp/B07PDXKSGJ/ref=sr_1_2?crid=1ISHR9ND9AYXA&keywords=MAW05M1BWT&qid=1677255565&s=home-garden&sprefix=maw05m1bwt%2Cgarden%2C76&sr=1-2&th=1",
        "https://www.amazon.com/Midea-EasyCool-Conditioner-Fan-Cools-Mechanical/dp/B07PFVKXYD/ref=sr_1_2?crid=1ISHR9ND9AYXA&keywords=MAW05M1BWT&qid=1677255565&s=home-garden&sprefix=maw05m1bwt%2Cgarden%2C76&sr=1-2&th=1",
        "https://www.amazon.com/Windmill-Air-Conditioner-Auto-Dimming-Voice-Enabled/dp/B08XN36B1B/ref=sr_1_1?crid=1GLIITHG5KKLF&keywords=B08XN36B1B&qid=1677255730&s=home-garden&sprefix=b08xn36b1b%2Cgarden%2C104&sr=1-1",
        "https://www.amazon.com/Soleus-Air-Exclusive-Conditioner-Putting/dp/B085P28D2S/ref=sr_1_3?crid=13QAHTKBWVS41&keywords=LW2217IVSM&qid=1677255761&s=home-garden&sprefix=lw2217ivsm%2Cgarden%2C70&sr=1-3",
        "https://www.amazon.com/LG-LW2516ER-Window-Mounted-Conditioner-Control/dp/B01D3FOCT8/ref=sr_1_2?crid=13QAHTKBWVS41&keywords=LW2217IVSM&qid=1677255761&s=home-garden&sprefix=lw2217ivsm%2Cgarden%2C70&sr=1-2",
        "https://www.amazon.com/Dreo-Inverter-Conditioner-Installation-Certified/dp/B09V1BBWS9/ref=sr_1_1?crid=2ZI695V67WYWT&keywords=DR-HAC002+G&qid=1677255790&s=home-garden&sprefix=dr-hac002+g%2Cgarden%2C85&sr=1-1"
    ]

    mandatory_pac_href_list = [
        "https://www.amazon.com/Midea-Conditioner-Dehumidifier-Fan-Cools-Assistant/dp/B087CQVC9G/ref=sr_1_3?crid=1F7HFEAW8Z4SR&keywords=MAP12S1TBL&qid=1677255849&s=home-garden&sprefix=map12s1tbl%2Cgarden%2C176&sr=1-3&th=1",
        "https://www.amazon.com/Midea-Conditioner-Dehumidifier-Fan-Cools-Assistant/dp/B087CQVC9G/ref=sr_1_3?crid=1F7HFEAW8Z4SR&keywords=MAP12S1TBL&qid=1677255849&s=home-garden&sprefix=map12s1tbl%2Cgarden%2C176&sr=1-3&th=1",
        "https://www.amazon.com/Midea-Conditioner-Dehumidifier-Fan-Cools-Assistant/dp/B091CKVY9F/ref=sr_1_3?crid=1F7HFEAW8Z4SR&keywords=MAP12S1TBL&qid=1677255849&s=home-garden&sprefix=map12s1tbl%2Cgarden%2C176&sr=1-3&th=1",
        "https://www.amazon.com/MIDEA-MAP05R1WT-Portable-Conditioner-Dehumidifier/dp/B09D3GW4V4/ref=sr_1_1?crid=9OSGP8Y7MUCL&keywords=MAP05R1WT&qid=1677255922&s=home-garden&sprefix=map05r1wt%2Cgarden%2C99&sr=1-1&th=1",
        "https://www.amazon.com/MIDEA-MAP05R1WT-Portable-Conditioner-Dehumidifier/dp/B09D3GW4V4/ref=sr_1_1?crid=9OSGP8Y7MUCL&keywords=MAP05R1WT&qid=1677255922&s=home-garden&sprefix=map05r1wt%2Cgarden%2C99&sr=1-1&th=1",
        "https://www.amazon.com/MIDEA-MAP05R1WT-Portable-Conditioner-Dehumidifier/dp/B0BB6DT495/ref=sr_1_1?crid=9OSGP8Y7MUCL&keywords=MAP05R1WT&qid=1677255922&s=home-garden&sprefix=map05r1wt%2Cgarden%2C99&sr=1-1&th=1",
        "https://www.amazon.com/MIDEA-MAP05R1WT-Portable-Conditioner-Dehumidifier/dp/B0BB6DT495/ref=sr_1_1?crid=9OSGP8Y7MUCL&keywords=MAP05R1WT&qid=1677255922&s=home-garden&sprefix=map05r1wt%2Cgarden%2C99&sr=1-1&th=1",
    ]


    #main(["https://www.amazon.com/s?k=dehumidifiers&i=garden&rh=n%3A267557011&page=","&qid=1676919652&ref=sr_pg_"], "Dehumidifier", 10, mandatory_dehum_href_list, days_back(10)) #TODO change the page number back
    #main(["https://www.amazon.com/s?k=window+air+conditioners&i=garden&page=","&crid=2R6D13IPHMWLU&qid=1677255230&sprefix=window+air%2Cgarden%2C92&ref=sr_pg_"], "WindowAC", 10, mandatory_wac_href_list, days_back(10))
    #main(["https://www.amazon.com/s?k=portable+air+conditioners&i=garden&page=","&crid=272AICN8B7H2J&qid=1677255334&sprefix=portable+air+conditioners%2Cgarden%2C81&ref=sr_pg_"], "PortableAC", 1, mandatory_pac_href_list, days_back(60))
    
    
    main(["https://www.amazon.com/Best-Sellers-Home-Kitchen-Portable-Air-Conditioners/zgbs/home-garden/1193678/ref=zg_bs_pg_", "_home-garden?_encoding=UTF8&pg="], "PortableAC top 100", 2, [], days_back(1))
    """
    main(["https://www.amazon.com/s?k=electric+kettle&i=garden&page=", "&crid=3REQG2ZDL2RMX&qid=1705879264&sprefix=electric+kettle%2Cgarden%2C111&ref=sr_pg_"], "Electric Kettle", 10, [], days_back(1000))