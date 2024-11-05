import random

from scrapingbee import ScrapingBeeClient
import time
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import pandas as pd
import inspect

import os
import sys


# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the secret_api_keys folder to the path
sys.path.append(os.path.join(current_dir, "..", "..", "secret_api_keys"))

import api_keys

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80


def get_product_hrefs_worker(n, q):
    """ This is a worker that will be used to incorporate multithreading. Using multi-threading because
        ScrapingBee lets us send 10 requests at a time.
        int n: Worker ID
        Queue q: queue from which to receive data"""

    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                x = get_product_hrefs(data)
                print(x)
                global product_hrefs_q
                for item in x:
                    product_hrefs_q.put(item)
                print("Success")
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

def get_product_hrefs(url, retries=0):
    MAX_RETRIES = 5
    if retries > MAX_RETRIES:
        return
    
    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    print("I made it here")
    # Next request the web page through ScrapingBee. provides response.status and response.content
    try:
        response = client.get(url,
                            params={
                                "render_js": False,
                                "timeout": 30000
                            },
                            timeout=35)
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        print("Couldn't get data from", url)
        return get_product_hrefs(url, retries + 1)

    print('Response HTTP Status Code: ', response.status_code)
    print("I made it here 2")
    if response.status_code == 200:
        # Turn the response.content into a BeautifulSoup object and extract the hrefs
        soup = BeautifulSoup(response.content, 'html.parser')
        href_soup = soup.find_all("a", {"class", "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
        #href_soup = soup.find_all("a", {"class", "a-link-normal"})
        if href_soup != []:
            return parse_href_soup(href_soup)
        else:
            return get_product_hrefs(url, retries + 1)
    
    elif response.status_code == 429:
        print("Too many requests, sleeping for 5 seconds")
        time.sleep(5)
        return get_product_hrefs(url, retries)
    
    elif response.status_code != 200:
        return get_product_hrefs(url, retries + 1)
    
    else:
        print("Failed to get data from", url)
    

def parse_href_soup(href_soup):
    href_and_bool = []
    # Parse the href into the scraping target url, add it to the queue
    for soup_item in href_soup:
        href = soup_item['href']
        href_and_bool += [["https://www.amazon.com" + href, True]]
    return href_and_bool

def get_product_dictionary_worker(n, q):
    """ This is a worker that will be used to incorporate multithreading. Using multi-threading because
        ScrapingBee lets us send 10 requests at a time.
        int n: Worker ID
        Queue q: queue from which to receive data"""

    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                x = get_product_dictionary(data)
                print(x)
                global product_dictionary_list
                product_dictionary_list[n] += [x]
                print("Success")
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

def get_product_dictionary(url_and_page_bool, retries=0):

    MAX_RETRIES = 5
    if retries > MAX_RETRIES:
        return
    
    url = url_and_page_bool[0]
    print("heres the url", url)
    page_bool = url_and_page_bool[1]
    print("heres the page bool", page_bool)
    client = ScrapingBeeClient(api_key=scrapingbee_API_key)
    try:
        response = client.get(
                                url,
                                params={
                                    "render_js": False,
                                    "timeout": 30000
                                },
                                timeout=35
                            )
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        print("Couldn't get data from", url)
        return get_product_dictionary(url_and_page_bool, retries + 1)
    
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # TODO should be a soup check here to make sure that we actually got the product page
        if page_bool:
            check_for_product_derivatives(soup, url)
        return parse_product_soup(soup, url)

    elif response.status_code == 429:
        print("Too many requests, sleeping for 5 seconds")
        time.sleep(5)
        return get_product_dictionary(url_and_page_bool, retries)
    
    elif response.status_code != 200:
        return get_product_dictionary(url_and_page_bool, retries + 1)
    else:
        print("Failed to get data from", url)
        

def check_for_product_derivatives(soup, url):
    """ Checks to see if the product has a derivative. If it does, it adds the derivative to the queue
        BeautifulSoup soup: The soup of the product page"""

    # Check to see if there is a button to click to see more products
    try:
        button_group = soup.find("ul", {"class", "a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare"})
        print(button_group)
        buttons = button_group.find_all("li")
        number_of_buttons = len(buttons)
        print(number_of_buttons)
        for index, button in enumerate(buttons):
            try:
                asin = button["data-defaultasin"]
                href_of_derivative = "https://www.amazon.com/dp/" + asin
                print(href_of_derivative)
                if asin != "":
                    product_hrefs_q.put([href_of_derivative, False])
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                print("couldn't get button for", button)
                
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        print("no extra buttons")
    
def parse_product_soup(soup, url):

    # asin
    try:
        asin = soup.find("input", {"id": "attach-baseAsin"})['value']
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        asin = ""
    #get the model number
    try:
        product_information = soup.find_all("table", {"id": "productDetails_detailBullets_sections1"})
    except Exception as e:
        try:
            product_information = soup.find_all("table", {"id": "productDetails_techSpec_section_1"})
        except Exception as e2:
            print(e)
            print(e2)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            product_information = []
            
    
    # get the product image
    try:
        product_image = soup.find("img", {"id": "landingImage"})["src"]
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        product_image = ""
    
        
    model_number = ""
    for table in product_information:
        for tag in table.find_all("tr"):
            
            try:
                model_number = tag.text.split("Item model number")[1].strip().split(" ")[0]
                
            except Exception as e:
                print(e)
                current_line = inspect.currentframe().f_lineno
                print(f"Current line number: {current_line}")
                if asin != "":
                    model_number = "ASIN: " + asin
                else:
                    model_number = ""
    
    #get the price
    try:
        price = soup.find("span", {"class": "a-price aok-align-center"}).find("span", {"class": "a-offscreen"}).text.strip()
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        price = ""
    
    if price == "":
        try:
            price = soup.find("div", {"id": "corePrice_feature_div"}).find("span", {"class": "a-offscreen"}).text.strip()
        except Exception:
            try:
                price = soup.find("input", {"id": "attach-base-product-price"})["value"]
                if price == "0.0":
                    try:
                        price = soup.find("span", {"class": "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"}).text.strip()
                    except Exception as e:
                        print(e)
                        current_line = inspect.currentframe().f_lineno
                        print(f"Current line number: {current_line}")
                        price = ""
            except Exception:
                try:
                    price = soup.find("span", {"class": "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"}).text.strip()
                except Exception as e:
                    print(e)
                    current_line = inspect.currentframe().f_lineno
                    print(f"Current line number: {current_line}")
                    price = ""
    
    # get model description
    try:
        model_description = soup.find("h1", {"id": "title"}).text.strip()
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        model_description = ""

    # get manufacturer
    try:
        manufacturer = soup.find("a", {"id": "bylineInfo"}).text.strip().split("Visit the ")[-1]
        manufacturer = manufacturer.split(" Store")[0]
        if "Brand: " in manufacturer:
            manufacturer = manufacturer.split("Brand: ")[-1]

    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        manufacturer = ""

    global appliance_type_global

    product_dictionary = {
        "Type": appliance_type_global,
        "Store": "Amazon.com",
        "Manufacturer": manufacturer,
        "Model No.": model_number,
        "Price": price,
        "Model Description": model_description,
        "sku": asin,
        "url": url,
        "product_image": product_image,
        "page_number": 1
    }
    print(product_dictionary)
    return product_dictionary


product_hrefs_q = Queue(maxsize=0)
starting_search_results_q = Queue(maxsize=0)
product_dictionary_list = [[] for i in range(CONCURRENCY)]
appliance_type_global = ""


def main(start_url_list, appliance_type, number_of_pages, guaranteed_product_hrefs):

    global product_hrefs_q
    product_hrefs_q = Queue(maxsize=0)

    global starting_search_results_q
    starting_search_results_q = Queue(maxsize=0)

    global product_dictionary_list
    product_dictionary_list = [[] for i in range(CONCURRENCY)]

    global appliance_type_global
    appliance_type_global = appliance_type

    for href in guaranteed_product_hrefs:
        product_hrefs_q.put([href, True])
        
    for page_number in range(1, number_of_pages + 1):
        starting_search_results_q.put(str(start_url_list[0]) + str(page_number) +str(start_url_list[1]) + str(page_number))
    
    # Create the get href threads
    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_product_hrefs_worker, args=(i, starting_search_results_q))]  
    # Start the get href threads
    for thread in threads:
        thread.start()
    # wait til the threads are finished
    for thread in threads:
        thread.join()
    
    # create the get product_dictionary threads
    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_product_dictionary_worker, args=(i, product_hrefs_q))]
    # start the get model number threads
    for thread in threads:
        thread.start()
    # wait til the threads are finished
    for thread in threads:
        thread.join()


    dataframe_to_export = pd.DataFrame()
    for my_list in product_dictionary_list:
        
        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)

        print(my_list)
        #convery list of dictionaries to pandas dataframe
        dataframe_to_export = dataframe_to_export._append(pd.DataFrame(my_list), ignore_index=True)

    dataframe_to_export = dataframe_to_export.drop_duplicates()

    
    dataframe_to_export.to_excel("outputs/Product Lists/" + "Amazon.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    return dataframe_to_export

if __name__ == "__main__":
    """mandatory_href_list = [
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B08ZMY8BC8/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B07NRC42PJ/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B09155CW3S/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B09155CW3S/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B091BYVD2W/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B0915DV55B/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1",
        "https://www.amazon.com/Midea-Dehumidifier-Ft-Compact-Basements-Medium-sized/dp/B0866XLRTX/ref=sr_1_1?keywords=MAD20S1QWT&qid=1677006036&sr=8-1&th=1"
    ]
    main(["https://www.amazon.com/s?k=dehumidifiers&i=garden&rh=n%3A267557011&page=","&qid=1676919652&ref=sr_pg_"], "Dehumidifier", 1, mandatory_href_list) #TODO change the page number back
    """
    
    main(["https://www.amazon.com/s?k=electric+kettle&i=garden&page=", "&crid=3REQG2ZDL2RMX&qid=1705879264&sprefix=electric+kettle%2Cgarden%2C111&ref=sr_pg_"], "Electric Kettle", 10, [])