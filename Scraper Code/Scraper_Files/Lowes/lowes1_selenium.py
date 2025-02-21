# use selenium webdriver to scrape lowes.com

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from time import sleep
from queue import Queue
from threading import Thread
import lowes1

from tqdm import tqdm

import math

    

def getDriver():
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    # Avoiding detection
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome()
    return driver


"""
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
"""

def product_parser(soup, appliance_type):
    
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
            "Type": appliance_type,
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
    
    return product_dictionary_list
    
    

def main(starting_url, number_of_pages, appliance_type):
    
    
    starting_url_list = []
    
    for i in range(number_of_pages):
        if i == 0:
            starting_url_list.append(starting_url)
        else:
            starting_url_list.append(starting_url + "?offset=" + str(i*24))
            
    
    
    driver = getDriver()
    
    product_dictionary_list = []
    
    for url in starting_url_list:
        driver.get(url)
        #scroll to bottom of page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        parsed_soup = product_parser(soup, appliance_type)
        product_dictionary_list = product_dictionary_list + parsed_soup
        
    
    print(product_dictionary_list)
    
    dataframe_to_export = pd.DataFrame(product_dictionary_list)

    dataframe_to_export.drop_duplicates(subset=["url"], inplace=True)
    dataframe_to_export.to_excel("outputs/Product Lists/" + "Lowes.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    return dataframe_to_export

if __name__ == "__main__":
    
    start_url, number_of_pages, appliance_type = "https://www.lowes.com/search?searchTerm=top+load+impeller+washer", 5, "Top Load Impeller"
    main(start_url, number_of_pages, appliance_type)