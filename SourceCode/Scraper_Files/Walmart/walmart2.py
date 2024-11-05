# This is just goin to get all the model numbers that we got in walmart1
import pandas as pd
from scrapingbee import ScrapingBeeClient
from http import client
import json
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
import time
import random
import requests
import re
import inspect

import walmart1_5
from secret_api_keys import api_keys

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

    url_to_scrape = "https://www.walmart.com/reviews/product/" + str(product_dictionary["sku"]) + "?sort=relevancy&page=" + str(product_dictionary["page_number"])

    # print(url_to_scrape)

    MAX_RETRIES = 1
    if retries > MAX_RETRIES:
        return

    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    try:

        response = client.get(
            url_to_scrape,
            params={
                "render_js": 'true',
                "premium_proxy": 'true',
                "block_resources": 'false',
                "timeout": 30000,
                'js_scenario':{"strict": False,
                    "instructions": [
                        {"wait": 1000},
                        {"click": ".bw0.bg-white.pointer.underline.f6"},
                        {"wait": 1000},
                        {"click": ".f6.mid-gray.pl1.pr3.pv2.relative.pointer.hover-bg-washed-primary"},
                        {"wait": 2000}
            ]}
            },
            timeout=30
        )

    except Exception as e:
        print(e)
        return get_reviews(product_dictionary, retries+1)

    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')
        review_cards = soup.find_all("div", class_="flex flex-column align-start") # May need to change this when walmart changes their website
        # print("RCARDS", review_cards)

        # with open("scrapingbee_response.html", "w", encoding="utf-8") as file:
        #     file.write(soup.prettify())

        if review_cards == []:
            return get_reviews(product_dictionary, retries+1)
        else:
            return parse_soup(soup, product_dictionary)
    
    elif response.status_code == 429:
        print("Too many requests")
        time.sleep(5)
        return get_reviews(product_dictionary, retries)
    
    elif response.status_code != 200:
        print('sth went wrong')
        print(response.status_code)
        print("Response content:", response.content)
        return get_reviews(product_dictionary, retries+1)
    
    else:
        print("Couldn't get reviews for", url_to_scrape)

def parse_soup(soup, product_dictionary):

    review_dictionary_list = []
    
    # the class name changed on walmart's website 2/2/24
    review_cards = soup.find_all("div", class_="flex flex-column align-start") # May need to change this when walmart changes their website
    
    for review in review_cards:

        #get star rating
        try:
            star_rating = int(review.find("span", {"class": "w_iUH7"}).text.strip()[0])
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            star_rating = ""

        # Get review data
        try: 
            date_string = review.find("div", {"class": "f7 gray mt1"}).text.strip()
            review_date = datetime.strptime(date_string, "%m/%d/%Y")
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_date = ""
        
        # Get review title
        try:
            # review_title = review.find("div", {"class": "f6 mid-gray lh-copy"}).find("div", {"class": "f5 mb2"}).text.strip()
            # if review_title == "":
            review_title = review.find("h3", {"class": "w_kV33 w_Sl3f w_mvVb f5 b"}).text.strip()
            print(review_title)
            
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_title = ""
        
        # Get review text
        try:
            review_text = review.find("span", {"class": "tl-m db-m"}).text.strip()
            print(review_text)
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_text = ""
        
        # Get review author

        try:
            review_author = review.find("span", {"class": "f7 b mv0"}).text.strip()
            
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_author = ""

        # Get review syndication
        try:
            review_syndication = review.find("div", {"class": "b ph1 dark gray"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_syndication = ""

        # Get Verified Purchase

        try:
            verified_purchase = review.find("span", {"class": "b f7 dark-gray"}).text.strip() 
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            verified_purchase = ""
        
        review_dictionary = {
            "Type": product_dictionary["Type"],
            "Store": product_dictionary["Store"],
            "Manufacturer": product_dictionary["Manufacturer"],
            "Model No.": product_dictionary["Model No."],
            "Price": product_dictionary["Price"],
            "Model Description": product_dictionary["Model Description"],
            "sku": str(product_dictionary["sku"]),
            "url": product_dictionary["url"],
            "product_image": product_dictionary["product_image"],
            "star_rating": star_rating,
            "review_title": review_title,
            "review_text": review_text,
            "review_date": review_date,
            "review_author": review_author,
            "original_review_syndication": review_syndication,
            "recommended": "", #TODO see if this is available
            "verified_purchase_badge": verified_purchase,
            "image_list": "" # this info not available on walmart
        }

        review_dictionary_list += [review_dictionary]

    try:
        check_if_need_next_page(product_dictionary, review_dictionary_list)
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        
    
    return review_dictionary_list
        
def check_if_need_next_page(product_dictionary, review_dictionary_list):

    date_list = []
    for review_dictionary in review_dictionary_list:
        if review_dictionary["review_date"] != "":
            date_list += [review_dictionary["review_date"]]


    if len(date_list) == 0:
        return
        
    
    if product_dictionary["page_number"] > 100:
        print("Already scraped 100 pages, if you want to scrape more pages, change line 212")
        return
    
    min_date = min(date_list)

    # if min_date newer than n_days_ago, then get next page
    if min_date > n_days_ago_global:
        product_dictionary["page_number"] += 1
        global product_dictionary_q
        product_dictionary_q.put(product_dictionary)

def days_back(n_days):
    # input: integer n_days (number of days to go back)
    # output: datetime n_days_ago (round to the start of the day)

    todays_date = datetime.now()
    n_days_ago = (todays_date - timedelta(days=n_days)).replace(hour=0, minute=0, second=0, microsecond=0)
    print("Scraping reviews going back until", n_days_ago)
    return n_days_ago

def excelSheetToDf(fileName, sheetName):
    """
    input: string fileName: name of excel file ending in .xlsx
           string sheetName: name of the sheet you want to pull from fileName
    output: pandas dataframe df: uses the first row in the excel file as headers
    """
    excel_file = pd.ExcelFile(fileName)
    df = excel_file.parse(sheetName)
    return df


product_dictionary_q = Queue(maxsize=0)
review_dictionary_list = [[] for i in range(CONCURRENCY)]
n_days_ago_global = ""

def main(starting_url, appliance_type, number_of_pages, n_days_ago):

    global product_dictionary_q
    product_dictionary_q = Queue(maxsize=0)

    global review_dictionary_list
    review_dictionary_list = [[] for i in range(CONCURRENCY)]

    global n_days_ago_global
    n_days_ago_global = n_days_ago

    starting_dataframe = walmart1_5.main(starting_url, number_of_pages, appliance_type)


    for index, row in starting_dataframe.iterrows():
        product_dictionary_q.put(row.to_dict())

    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_reviews_worker, args=(i, product_dictionary_q))]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("I made it here w2")
    dataframe_to_export = pd.DataFrame()
    for my_list in review_dictionary_list:
        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)

        dataframe_to_export = dataframe_to_export._append(my_list, ignore_index=True)

    dataframe_to_export.to_excel("outputs/Reviews/" + "Walmart.com " + appliance_type + " Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)

    return dataframe_to_export



if __name__ == "__main__":
    main("https://www.walmart.com/browse/air-conditioners/window-air-conditioners/1072864_133032_1231458_133026_587566?facet=retailer_type%3AWalmart&page=", "WindowAC", 1, days_back(100))