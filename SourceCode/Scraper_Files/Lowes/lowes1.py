import json
from queue import Queue
from threading import Thread
import pandas as pd
from time import sleep
from scrapingbee import ScrapingBeeClient
from datetime import datetime
import random
from bs4 import BeautifulSoup
import requests

import os
import sys
original_sys_path = sys.path.copy()
sys.path = original_sys_path + [os.path.dirname(os.path.dirname(os.path.dirname(__file__)))]
from secret_api_keys import api_keys
sys.path = original_sys_path

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80


def get_products_worker(n,q):
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                print("Getting json...")
                x = get_products(data)
                print("Got json!")

                # put the reviews into the global variable review_result where each thread will have a designated index
                # where it can safely append new revuews
                global product_dictionaries
                for my_dict in x:
                    product_dictionaries[n] += [my_dict]
                print("Great Success")
                q.task_done()
            except Exception:
                print("Couldn't get data from", data)
                q.task_done()
        except Exception:
            print("Thread", n, "has joined")
            break

def get_products(url_to_scrape, retries=0):
    MAX_RETRIES = 10
    if retries > MAX_RETRIES:
        return
    
    try:
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': scrapingbee_API_key,
                'url': url_to_scrape,
                'block_resources': 'false',
                'stealth_proxy': 'true',
                'js_scenario': '{"instructions":[{"wait_for":"#listItems"},{"wait":15000}]}', 
            },
            timeout=60 
        )
    except Exception as e:
        print("Error:", e)
        return get_products(url_to_scrape, retries+1)

    print(response.status_code)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        return soup_parser(soup)

    elif response.status_code == 429:
        print("Too many requests, waiting 5 seconds")
        sleep(5)
        get_products(url_to_scrape, retries)

    elif response.status_code != 200:
        return get_products(url_to_scrape, retries+1)

    else:
        print("Couldn't get products off", url_to_scrape)
        return

def soup_parser(soup):
    #needs to return a list of dictionaries
    product_dictionary_list = []
    for i in range(1, 25):
        product_tiles = soup.find_all("div", {"data-tile": str(i)})
        manufacturer = ""
        model_number = ""
        model_description = ""
        price = ""
        url = ""
        sku = ""
        product_image = ""

        for tile in product_tiles:
            try:
                manufacturer = tile.find("span", {"data-selector": "splp-prd-brd-nm"}).text.strip()
                
            except Exception:
                manufacturer = manufacturer

            try:
                model_number = tile.find("span", {"class": "tooltip-custom"}).text.strip().split("Model #")[-1]
                
            except Exception:
                model_number = model_number

            try:
                model_description = tile.find("span", {"class": "description-spn"}).text.strip()
            except Exception:
                model_description = model_description
            
            try:
                price = tile.find("div", {"data-selector": "splp-prd-act-$"}).text.strip()
            except Exception:
                try:
                    price = tile.find("div", {"data-selector": "splp-prd-$"}).text.strip()
                except Exception:
                    price = price
            
        
            if url == "":
                try:
                    url = "https://www.lowes.com" + str(tile.find("a")["href"])
                except Exception:
                    url = url
            
            if product_image == "":
                try:
                    product_image = tile.find("a").find("div").find("div").find("img")["src"]
                    print(product_image)
                except Exception as e:
                    print(e)
                    product_image = product_image
                
            
            try:
                sku = url.split("/")[-1]
            except Exception:
                sku = sku
            

        print(manufacturer, model_number, model_description, price, url)

        product_dictionary = {
            "Type": appliance_type_global,
            "Store": "Lowes.com",
            "Manufacturer": manufacturer,
            "Model No.": model_number,
            "Price": price,
            "Model Description": model_description,
            "sku": sku,
            "url": url,
            "product_image": product_image,
        }
        
        
       
        product_dictionary_list += [product_dictionary]
    
    print(product_dictionary_list)
    
    return product_dictionary_list

product_dictionaries = [[] for i in range(CONCURRENCY)]
starting_url_q = Queue(maxsize=0)
appliance_type_global = ""

def main(starting_url, number_of_pages, appliance_type):
    #return the lowes input json
    global starting_url_q
    starting_url_q = Queue(maxsize=0)

    global product_dictionaries
    product_dictionaries = [[] for i in range(CONCURRENCY)]

    global appliance_type_global
    appliance_type_global = appliance_type

    threads = []
    for i in range(number_of_pages):
        if i == 0:
            starting_url_q.put(starting_url)
        else:
            starting_url_q.put(starting_url + "&offset=" + str(i*24))

    for i in range(CONCURRENCY):
        threads += [Thread(target=get_products_worker, args=(i,starting_url_q))]

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    dataframe_to_export = pd.DataFrame()
    for my_list in product_dictionaries:
        #convery list of dictionaries to pandas dataframe

        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)
        
        dataframe_to_export = dataframe_to_export._append(pd.DataFrame(my_list), ignore_index=True)

    dataframe_to_export.drop_duplicates(subset=["url"], inplace=True)
    dataframe_to_export.to_excel("outputs/Product Lists/" + "Lowes.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    return dataframe_to_export

if __name__ == "__main__":
    main("https://www.lowes.com/pl/Dehumidifiers-Humidifiers-dehumidifiers-Heating-cooling/4294620974",3,"Dehumidifier")