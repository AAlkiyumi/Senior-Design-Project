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

import walmart1
from secret_api_keys import api_keys

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80



def get_model_number_worker(n, q):
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                print("Getting json...")
                x = get_model_number(data)
                print("Got json!")

                # put the reviews into the global variable review_result where each thread will have a designated index
                # where it can safely append new revuews
                global updated_product_dictionary_list
                updated_product_dictionary_list[n] += [x]
                print("Great Success")
                q.task_done()
            except Exception as e:
                print(e)
                print("Couldn't get data from", data)
                q.task_done()
        except Exception:
            print("Thread", n, "has joined")
            break

def get_model_number(product_dictionary, retries=0):
    MAX_RETRIES = 3
    if retries > MAX_RETRIES:
        product_dictionary["Model No."] = ""
        # product_dictionary["Manufacturer"] = ""
        return product_dictionary
        

    try:
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': scrapingbee_API_key,
                'url': product_dictionary["url"],
                'block_resources': 'false',
                'stealth_proxy': 'true', 
                'wait': '5000'
            },
            timeout=60
        )   

    except Exception as e:
        print(e)
        #print line number
        print("line #", inspect.currentframe().f_back.f_lineno)

        return get_model_number(product_dictionary, retries+1)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        with open("walmart1_5_scrapingbee_response.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        # TODO: a check
        specification_tags = soup.find_all("div", {"class": "pb2"})
        if len(specification_tags) > 0:
            return soup_parser(soup, product_dictionary)
        else:
            return get_model_number(product_dictionary, retries+1)

    elif response.status_code == 429:
        print("429 error, sleeping for 5 seconds")
        time.sleep(5)
        return get_model_number(product_dictionary, retries+1)
    else:
        print("Error", response.status_code)
        return get_model_number(product_dictionary, retries+1)

def soup_parser(soup, product_dictionary):

    
    
    # try to get the model number and brand from the json data
    
    
    # find the script tag that contains the json data
    script_tag_text = soup.find("script", {"type": "application/ld+json"}).text
    # load this into a dict using json
    script_tag_dict = json.loads(script_tag_text)
    # get the model number
    try:
        product_dictionary["Model No."] = script_tag_dict["model"]
    except Exception as e:
        print(e)
        product_dictionary["Model No."] = ""
    
    try:
        product_dictionary["Manufacturer"] = script_tag_dict["brand"]["name"]
    except Exception as e:
        print(e)
        # product_dictionary["Manufacturer"] = ""
        
      
      
    # if the model number is not in the json data, try to get it from the specifications
    if product_dictionary["Model No."] == "":
        
        specification_tags = soup.find_all("div", {"class": "pb2"})
        print(specification_tags)

        for specification_tag in specification_tags:
            print(specification_tag)

            try:
                specification_title = specification_tag.find("h3").text.strip()
                specification_value = specification_tag.find("div").find("span").text.strip()
            
                if "model" in specification_title.lower():
                    product_dictionary["Model No."] = specification_value
                    break
                
                
            except Exception as e:
                print(e)
                
    # if the model number is still blank try to get it from part number
    if product_dictionary["Model No."] == "":
        
        try:
            specification_tags = soup.find_all("div", {"class": "pb2"})
            print(specification_tags)

            for specification_tag in specification_tags:
                print(specification_tag)

                try:
                    specification_title = specification_tag.find("h3").text.strip()
                    specification_value = specification_tag.find("div").find("span").text.strip()
                
                    if "part" in specification_title.lower():
                        product_dictionary["Model No."] = specification_value
                        break
                    
                    
                except Exception as e:
                    print(e)
                    
        except Exception as e:
                print(e)
    
    return product_dictionary


product_dictionary_q = Queue(maxsize=0)
updated_product_dictionary_list = [[] for i in range(CONCURRENCY)]
def main(starting_url, number_of_pages, appliance_type):

    global product_dictionary_q
    product_dictionary_q = Queue(maxsize=0)

    global updated_product_dictionary_list
    updated_product_dictionary_list = [[] for i in range(CONCURRENCY)]

    starting_df = walmart1.main(starting_url, number_of_pages, appliance_type)
    
    print("I made it here w1.5")
    # put the rows of the dataframes into a queue

    for index, row in starting_df.iterrows():
        product_dictionary_q.put(row.to_dict())

    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_model_number_worker, args=(i, product_dictionary_q))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    dataframe_to_export = pd.DataFrame()
    for my_list in updated_product_dictionary_list:
        #convery list of dictionaries to pandas dataframe
        
        # remove None values from the list
        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)  
        # append my_list of dictionaries to the dataframe_to_export
        dataframe_to_export = dataframe_to_export._append(pd.DataFrame(my_list), ignore_index=True)

    dataframe_to_export.to_excel("outputs/Product Lists/" + "Walmart.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    
    return dataframe_to_export

if __name__ == "__main__":
    main("https://www.walmart.com/browse/air-conditioners/window-air-conditioners/1072864_133032_1231458_133026_587566?facet=retailer_type%3AWalmart&page=", 4, "WindowAC")