import pandas as pd
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import time
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import inspect

import copy

import bestbuy1
from secret_api_keys import api_keys

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80
#TODO: add in re to remove special characters from text variables

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
                    print(my_dict)
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
    MAX_RETRIES = 5
    if retries > MAX_RETRIES:
        return

    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    try:
        response = client.get(
            product_dictionary["url"],
            params={
                "render_js": True,
            },
            timeout=30
        )
    except Exception as e:
        print(e)
        return get_reviews(product_dictionary, retries+1)

    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')
        review_cards = soup.find_all("li", {"class": "review-item"})
        if review_cards == []:
            return get_reviews(product_dictionary, retries+1)
        else:
            return parse_soup(soup, product_dictionary)
    
    elif response.status_code == 429:
        print("Too many requests")
        time.sleep(5)
        return get_reviews(product_dictionary, retries)
    
    elif response.status_code != 200:
        return get_reviews(product_dictionary, retries+1)
    
    else:
        print("Couldn't get reviews for", product_dictionary["url"])

def parse_soup(soup, product_dictionary):
    review_dictionary_list = []
    review_cards = soup.find_all("li", {"class": "review-item"})
    for review in review_cards:
        try:
            star_rating = int(review.find("p", {"class": "visually-hidden"}).text[6])
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            star_rating = ""

        try: 
            review_title = review.find("h4", {"class": "c-section-title review-title heading-5 v-fw-medium"}).text.strip()

        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_title = ""
        
        try:
            review_text = review.find("div", {"class": "ugc-review-body"}).text.strip()
            
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_text = ""
        
        try:
            unparsed_date = review.find("time", {"class": "submission-date"})['title']
            review_date = datetime.strptime(str(unparsed_date), "%b %d, %Y %I:%M %p")
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_date = ""
        
        try:
            review_author = review.find("div", {"class": "ugc-author v-fw-medium body-copy-lg"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_author = ""
        
        try:
            recommendation = review.find("div", {"class": "ugc-recommendation"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            recommendation = ""
        
        if recommendation == "I would recommend this to a friend":
            recommendation = "yes"
        elif recommendation == "No, I would not recommend this to a friend":
            recommendation = "no"
        else:
            recommendation = ""
        

        try:
            verified_purchase_badge = review.find("button", {"data-track": "Verified Purchase Badge"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            verified_purchase_badge = ""
        
        try:
            owned_for_x_when_reviewed = review.find("div", {"class": "posted-date-ownership disclaimer v-m-right-xxs"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            owned_for_x_when_reviewed = ""

        try:
            image_list = []
            images = review.find_all("img")
            for image in images:
                try:
                    image_list += [image["src"]]
                except Exception as e:
                    print(e)
                    current_line = inspect.currentframe().f_lineno
                    print(f"Current line number: {current_line}")
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
            "original_review_syndication": "", #Not available, takes you to another site
            "recommended": recommendation,
            "verified_purchase_badge": verified_purchase_badge,
            "image_list": image_list,
            #owned_for_x only available on bestbuy will be dropped
            "owned_for_x_when_reviewed": owned_for_x_when_reviewed
        }
        review_dictionary_list += [review_dictionary]

        check_if_need_next_page(product_dictionary, review_dictionary_list)

    return review_dictionary_list
    
def check_if_need_next_page(product_dictionary, review_dictionary_list):

    review_date_list = []
    for review_dictionary in review_dictionary_list:
        review_date_list += [review_dictionary["review_date"]]
    
    minimum_date = min(review_date_list)
    if minimum_date > n_days_ago_global:
        try:
            current_page_number = int(product_dictionary["url"].split("page=")[-1])
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            return

        if len(review_dictionary_list) >= 20:
            if current_page_number < 30:
                new_product_dictionary = copy.deepcopy(product_dictionary)
                new_product_dictionary["url"] = "page=".join(product_dictionary["url"].split("page=")[:-1]) + "page=" + str(current_page_number + 1)
                product_dictionary_q.put(new_product_dictionary)
            else:
                print("Already went back 30 pages, stopping")
        
        else:
            print("On last page already")


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

def main(start_url_list, appliance_type, number_of_pages, n_days_ago):
    
    global product_dictionary_q
    product_dictionary_q = Queue(maxsize=0)
    
    global review_dictionary_list
    review_dictionary_list = [[] for i in range(CONCURRENCY)]
    
    global n_days_ago_global
    n_days_ago_global = n_days_ago

    starting_dataframe = bestbuy1.main(start_url_list, appliance_type, number_of_pages)

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
    
    dataframe_to_export.to_excel("outputs/Reviews/" + "BestBuy.com " + appliance_type +" Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    
    # drop owned_for_x_when_reviewed column
    try:
        dataframe_to_export = dataframe_to_export.drop(columns=["owned_for_x_when_reviewed"], axis=1)
    except Exception as e:
        print(e)
    return dataframe_to_export

#just for testing purpose
if __name__ == "__main__":
    main(["https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=abcat0907004&cp=", "&id=pcat17071&iht=n&ks=960&list=y&sc=Global&st=categoryid%24abcat0907004&type=page&usc=All%20Categories"], "PortableAC", 1, days_back(30))