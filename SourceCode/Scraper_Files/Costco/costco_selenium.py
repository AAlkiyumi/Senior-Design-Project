# use selenium webdriver to scrape lowes.com

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import inspect
#from ScraperFiles.Costco import costco1
    

def getDriver():
    options = Options()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    # Avoiding detection
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    return driver

def get_model_number(html):

    soup = BeautifulSoup(html, 'html.parser')
    try:
        # model_number = soup.find("div", {"id": "product-body-model-number"}).find("span").text.strip()
        model_number = soup.find("div", {"id": "product-body-model-number","class":"model-number"}).text.strip().replace('Model', '').strip()


    except Exception as e:
        model_number = ""
        print(e)
    
    print(model_number)
    return model_number




def get_reviews(product_dictionary):
    
    review_dictionary_list_to_return = []
    
    
    
    url = product_dictionary["url"]
    global driver
    driver.get(url)

    

    try:
        product_dictionary["Model No."] = get_model_number(driver.page_source)
    except Exception as e:
        print(e)
        
    # START BACK UP HERE
    
    #nav-pdp-tab-header-13 > div.row.view-more-v2 > div > input
    # click the view more button
    sleep(5)
    try:
        view_more_buttons = driver.find_elements(By.XPATH, "//input[@value='View More']")
        view_more_buttons[-1].click()
        
        # scroll down a little
        driver.execute_script("window.scrollBy(0, " + str(400) + ");")
        sleep(4)
    except Exception as e:
        print(e)
    
    
    """<div class="bv-dropdown">  <div class="bv-dropdown-target"> <span id="bv-dropdown-select-reviews" class="bv-dropdown-label" aria-hidden="true"> Sort by: </span>   <button type="button" role="listbox" id="bv-dropdown-sort-by-reviews" class="bv-focusable" aria-haspopup="true" aria-expanded="false" aria-labelledby="bv-dropdown-reviews-menu bv-dropdown-select-reviews bv-dropdown-title-reviews"> <span id="bv-dropdown-title-reviews" class="bv-dropdown-title" role="option">   Most Relevant           </span> <span class="bv-dropdown-arrow" aria-hidden="true" role="presentation"> ▼ </span> <span id="bv-dropdown-reviews-menu" class="bv-off-screen">Menu</span> </button> </div> <select class="bv-select-cleanslate bv-dropdown-select" aria-hidden="true" aria-labelledby="bv-dropdown-select-reviews" tabindex="-1">  <option value="relevancy" selected=""> Most Relevant </option>  <option value="mostHelpful"> Most Helpful </option>  <option value="positive"> Highest to Lowest Rating </option>  <option value="negative"> Lowest to Highest Rating </option>  <option value="mostRecent"> Most Recent </option>  </select> </div>"""
    # hover over the dropdown button
    try:
        dropdown_button = driver.find_element(By.XPATH, "//div[@class='bv-dropdown']")
        hover = ActionChains(driver).move_to_element(dropdown_button)
        for i in range(3):
        
            try:
                hover.perform()
                sleep(3)
                
                #data-bv-dropdown-item-mostRecent
                # click the most recent button
                most_recent_button = driver.find_element(By.ID, "data-bv-dropdown-item-mostRecent") 
                most_recent_button.click()
                break
                
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    
    # for i in range(3):
        
    #     try:
    #         hover.perform()
    #         sleep(3)
            
    #         #data-bv-dropdown-item-mostRecent
    #         # click the most recent button
    #         most_recent_button = driver.find_element(By.ID, "data-bv-dropdown-item-mostRecent") 
    #         most_recent_button.click()
    #         break
            
    #     except Exception as e:
    #         print(e)
            
    # scroll down until you find the next page button
    """
    "BVRRContainer > div > div > div > "
    "div > div.bv-content-pagination > div > ul > "
    "li.bv-content-pagination-buttons-item.bv-content-pagination"
    "-buttons-item-next > a').click();
    """
    
    
    
    while True:
        
        try:
            
            sleep(1)
            review_dictionary_list_to_return += parse_soup(driver.page_source, product_dictionary)
            # click the next element button using css selector
            next_button = driver.find_element(By.CSS_SELECTOR, "#BVRRContainer > div > div > div > div > div.bv-content-pagination > div > ul > li.bv-content-pagination-buttons-item.bv-content-pagination-buttons-item-next > a")
            next_button.click()
            
            
        except Exception as e:
            
            print(e)
            break
            
    
    return review_dictionary_list_to_return



def went_back_far_enough_already(html):
    soup = BeautifulSoup(html, 'html.parser')

    review_containers = soup.find_all("div", {"itemprop": "review"})
    date_list = []
    for review in review_containers:
        try:
            review_date = review.find("span", {"class": "cgcreviewsubmitdate"}).text.strip()
            review_date = datetime.strptime(review_date, "%B %d, %Y")
            date_list.append(review_date)
        except Exception as e:
            print(e)
    
    # find oldest date in date list
    if len(date_list) == 0:
        return True
    oldest_date = min(date_list)

    global n_days_ago_global
    if oldest_date < n_days_ago_global:
        return True
    else:
        return False

    return True

    

def parse_soup(html, product_dictionary):

    soup = BeautifulSoup(html, 'html.parser')
    
    if product_dictionary["product_image"] == "":
        try:
            product_dictionary["product_image"] = soup.find("img", {"id": "productImage"})["src"]
        except Exception as e:
            print(e)
            product_dictionary["product_image"] = ""
    

    #going to return this at the end
    review_dictionary_list = []

    review_list = soup.find_all("li", {"itemprop": "review"})

    for review in review_list:
        
        try:
            star_rating = int(review.find("span", {"class": "bv-off-screen"}).text.strip()[0])
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            star_rating = ""
        
        try:
            review_title = review.find("h3", {"itemprop": "headline"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_title = ""

        try:
            review_text = review.find("div", {"class": "bv-content-summary-body-text"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_text = ""

        try:
            review_string = review.find("meta", {"itemprop": "dateCreated"})['content']
            review_date = datetime.strptime(review_string, "%Y-%m-%d")
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_date = ""

        
        try:
            specifications_card = soup.find("div", {"class": "product-info-specs body-copy"})
            #print(specifications_card.prettify())
            manufacturer = specifications_card.find("div", {"itemprop": "brand"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            manufacturer = ""
        
        try:
            review_author = review.find("div", {"class": "bv-content-header"}).find("span", {"itemprop": "name"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            review_author = ""
        
        try:
            verified_purchaser = review.find("li", {"class": "bv-badge bv-badge-content bv-badge-content-verifiedpurchaser"}).text.strip()
            # remove the leading * and white space *   Verified Purchaser
            verified_purchaser = verified_purchaser[1:].strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            verified_purchaser = ""
        
        try: 
            recommend_yes = review.find("div", {"class": "bv-content-data-recommend-yes"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            recommend_yes = ""

        try:
            recommend_no = review.find("div", {"class": "bv-content-data-recommend-no"}).text.strip()
        except Exception as e:
            print(e)
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
            recommend_no = ""
        
        if recommend_yes != "":
            recommendation = recommend_yes
        else:
            recommendation = recommend_no

        if "No" in recommendation:
            recommendation = "no"
        elif "Yes" in recommendation:
            recommendation = "yes"
        else:
            recommendation = ""
    
    
        

        review_dictionary = {
            "Type": product_dictionary["Type"],
            "Store": "Costco.com",
            "Manufacturer": manufacturer,
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
            "original_review_syndication": "", #TODO check for this
            "recommended": recommendation,
            "verified_purchase_badge": verified_purchaser,
            "image_list": [] #not available on costco.com
        }
        review_dictionary_list += [review_dictionary]
        print(review_dictionary)
        #check_if_need_next_page(product_dictionary)
    
    return review_dictionary_list
    


def get_product_dictionaries(driver, appliance_type):
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    
    # find all products in soup
    products = soup.find_all("div", {"class": "col-xs-6 col-lg-4 col-xl-3 product"})
    print(products)
    
    if products == []:
        products = soup.find_all("div", {"class": "product col-xs-12"})
        
    
    product_dictionary_list_to_return = []
    for product in products:
        
        # find sku input id = product_sku_ + wildcard
        try:
            sku = product.find("input", {"id": lambda l: l and l.startswith('product_sku')})["value"]
        except Exception as e:
            print(e)
            sku = ""
            
        # find model description <input id="product_name_4000113824" type="hidden" value="Hisense 50-pint Dehumidifier"/>
        try:
            model_description = product.find("input", {"id": lambda l: l and l.startswith('product_name')})["value"]
        except Exception as e:
            print(e)
            model_description = ""
    
        # get the product url <input id="product_name_4000113824" type="hidden" value="Hisense 50-pint Dehumidifier"/>
        try:
            url = product.find("div", {"class": "product-tile-set"})["data-pdp-url"] + "#nav-pdp-tab-header-13"
        except Exception as e:
            print(e)
            url = ""
        
        # get the price div class price
        try:
            # price = float(product.find("div", {"class": ""}).find("div", {"class": "price"}).text.strip()[1:])
            price = float(product.find("div", {"class": "price"}).text.strip()[1:].replace(',', ''))

        except Exception as e:
            print(e)
            price = ""
    
        # get the manufacturer
        try:
            manufacturer = model_description.split(" ")[0]
        except Exception as e:
            print(e)
            manufacturer = ""
            
        # get the product image
        try:
            product_image = product.find("a", {"class": "product-image-url"}).find("img")["src"]
        except Exception as e:
            print(e)
            product_image = ""
            
        new_product_dictionary = {
            "Type": appliance_type,
            "Store": "Costco.com",
            "Manufacturer": manufacturer,
            "Price": price,
            "Model No.": None,
            "Model Description": model_description,
            "sku": sku,
            "url":url,
            "product_image": product_image,
        }
        
        product_dictionary_list_to_return += [new_product_dictionary]
            
        
    return product_dictionary_list_to_return
        

    
    
    
    
    

driver = ""
n_days_ago_global = ""
def main(start_url, number_of_pages, appliance_type, n_days_ago):
    
    global n_days_ago_global
    n_days_ago_global = n_days_ago
    
    # product_dataframe = costco1.main(start_url, number_of_pages, appliance_type)
    # product_dictionary_list = product_dataframe.to_dict("records") ##to check

    global driver
    driver = getDriver()

    driver.get(start_url)
    # get product list
    input("login- Press enter to conitnue")
    
    for page_number in range(number_of_pages):
        
        if page_number == 0:
            product_dictionary_list = get_product_dictionaries(driver, appliance_type)
        else:
            print("Need to make scenario for more than one page")
            
    print(product_dictionary_list)
    #PICK BACK UP HERE
    prod_dataframe_to_exp = pd.DataFrame(product_dictionary_list)
    prod_dataframe_to_exp.to_excel("outputs/Product Lists/" + "Costco.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    
    review_dictionary_list = []
    for product_dictionary in product_dictionary_list:
        review_dictionary_list += get_reviews(product_dictionary)
    
    
    driver.close()
    
    # take the list of review dictionaries and convert it into a pandas dataframe
    dataframe_to_export = pd.DataFrame(review_dictionary_list)
    
    
    dataframe_to_export.to_excel("outputs/Reviews/" + "Costco.com " + appliance_type + " Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    return dataframe_to_export
    
    
    
    
if __name__ == "__main__":
    main("https://www.costco.com/CatalogSearch?dept=All&keyword=portable+air+conditioner", 1, "PortableAC", 365)