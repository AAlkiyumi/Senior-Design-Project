import pandas as pd
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import time
import json
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import inspect
import re
import os
import sys
original_sys_path = sys.path.copy()
sys.path = original_sys_path + [os.path.dirname(os.path.dirname(os.path.dirname(__file__)))]
from secret_api_keys import api_keys
sys.path = original_sys_path

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80

def get_product_dictionary_worker(n, q):
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                x = get_product_dictionaries(data)
                print(x)
                global product_dictionaries
                for my_dict in x:
                    product_dictionaries[n] += [my_dict]
                print("Success")
                q.task_done()
            except Exception as e:
                print(e)
                print("Couldn't get data from", data)
                q.task_done()
        except Exception:
            print("Thread", n, "has joined.")
            break

def get_product_dictionaries(url, retries=0):
    MAX_RETRIES = 5
    if retries > MAX_RETRIES:
        return

    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    try:
        response = client.get(
            url,
            params={
                'render_js': True,
                'wait': 5000
            },
            timeout=60
        )
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        return get_product_dictionaries(url, retries+1)

    print(response.status_code)
    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')
        product_card_list = soup.find_all("li", {"class": "sku-item"})
        if product_card_list == []:
            return get_product_dictionaries(url, retries+1)
        else:
            return parse_soup(soup)

    elif response.status_code == 429:
        print("Too many requests")
        time.sleep(5)
        return get_product_dictionaries(url, retries)

    elif response.status_code != 200:
        return get_product_dictionaries(url, retries+1)
    
    else:
        print("Couldn't get data from", url)

def parse_soup(soup):
    product_card_list = soup.find_all("li", {"class": "sku-item"})

    product_dictionaries_to_return = []
    for product_card in product_card_list:
        try:
            manufacturer_and_description = product_card.find("h4", {"class": "sku-title"}).text.strip()
            manufacturer = manufacturer_and_description.split(" - ")[0]
            if manufacturer.startswith("New!"):
                manufacturer = manufacturer.split("New!")[-1]
            model_description = (" - ").join(manufacturer_and_description.split(" - ")[1:])
            
        except Exception as e:
            manufacturer = ""
            model_description = ""
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")

        try:
            model_number = product_card.find("span", {"class": "sku-value"}).text.strip()
        except Exception as e:
            model_number = ""
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")

        try: 
            sku = product_card["data-sku-id"]
        except Exception as e:
            sku = ""
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        try:
            href = product_card.find("h4", {"class": "sku-title"}).find("a")["href"]
            try:
                split_href = href.split('/')
                new_url = "https://www.bestbuy.com/site/reviews/" + split_href[2] + "/" + split_href[-1].split("skuId=")[-1] \
                        + "?variant=A&skuId=" + split_href[-1].split("skuId=")[-1] + "&sort=MOST_RECENT&page=1"
                print(new_url)
                print("-" * 80)
            except Exception as e:
                print("EXCEPTION WITH HREF: ", href.split('/'))
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
        except Exception as e:
            print(e)
            new_url = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        try:
            price = product_card.find("div", {"class": "priceView-hero-price priceView-customer-price"}).find("span", {"aria-hidden": "true"}).text.strip()
        except Exception as e:
            price = ""
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            
        try:
            product_image = product_card.find("img", {"class": "product-image"})["src"]
        except Exception as e:
            product_image = ""
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")

        product_dictionary = {
            "Type": appliance_type_global,
            "Store": "BestBuy.com",
            "Manufacturer": manufacturer,
            "Model No.": model_number,
            "Price": price,
            "Model Description": model_description,
            "sku": sku,
            "url": new_url,
            "product_image": product_image
        }
        product_dictionaries_to_return += [product_dictionary]
    return product_dictionaries_to_return

product_dictionaries = [[] for i in range(CONCURRENCY)]
start_url_q= Queue(maxsize=0)
appliance_type_global = ""

def main(start_url_list, appliance_type, number_of_pages):
    global product_dictionaries
    product_dictionaries = [[] for i in range(CONCURRENCY)]

    global appliance_type_global
    appliance_type_global = appliance_type

    for i in range(number_of_pages):
        start_url_q.put(start_url_list[0] + str(i+1) + start_url_list[1])
    
    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_product_dictionary_worker, args=(i, start_url_q))]
    
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
    
    
    dataframe_to_export.to_excel("outputs/Product Lists/" + "BestBuy.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)

    return dataframe_to_export
    
if __name__ == "__main__":
    main(["https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=abcat0908002&cp=", "&id=pcat17071&iht=n&ks=960&list=y&sc=Global&st=categoryid%24abcat0908002&type=page&usc=All%20Categories"], "Dehumidifier", 3)    

