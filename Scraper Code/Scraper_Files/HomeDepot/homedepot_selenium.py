# # use selenium webdriver to scrape homedepot.com

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from time import sleep
from queue import Queue

from tqdm import tqdm

CONCURRENCY = 50

def getDriver():
    options = Options()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    # Avoiding detection
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    return driver


def parse_reviews(soup, product_dictionary):

    review_dictionary_list = []

    if product_dictionary["Manufacturer"] == "":
        try:
            product_dictionary["Manufacturer"] = soup.find("h2", {"class": "sui-font-bold sui-text-base sui-tracking-normal sui-normal-case sui-line-clamp-unset sui-text-primary"}).text.strip()
        except Exception:
            product_dictionary["Manufacturer"] = ""


    
    if product_dictionary["Model No."] == "":
        try:
            model_number_info = soup.find_all("h2", {"class": "product-info-bar__detail--7va8o"})
            for information in model_number_info:
                if "Model" in information.text.strip():
                    product_dictionary["Model No."] = information.text.strip().split("#")[-1].strip()
        except Exception:
            product_dictionary["Model No."] = ""

    if True:  #used to say if product_dictionary["sku"] == "":
        try:
            model_number_info = soup.find("h2", {"class": "product-info-bar__detail--7va8o"})
            for information in model_number_info:
                if "Internet" in information.text.strip():
                    product_dictionary["sku"] = information.text.strip().split("#")[-1].strip()
        except Exception:
            product_dictionary["sku"] = ""
        
    if product_dictionary["Price $"] == "":
        try:
            price_list = soup.find_all("div", {"class": "price"})
            product_dictionary["Price $"] = price_list[0] + price_list[1] + "." + price_list[2]
        except Exception:
            product_dictionary["Price $"] = ""



    review_cards = soup.find_all("div", {"class": "review_item"})

    print("REVIEW CARDS FOUND = ", len(review_cards))
    for review_card in review_cards:

        try:
            star_rating = int(review_card.find("span", {"class": "stars--c43xm"})['style'].split(" ")[-1][:-2]) // 20
        except Exception:
            try:
                star_rating = int(review_card.find("span", {"class": "stars--c43xm"})['style'].split(":")[-1][:-2]) // 20
            except Exception:
                star_rating = ""
        
        try:
            review_title = review_card.find("span", {"class": "review-content__title"}).text.strip()
    
        except Exception:
            review_title = ""
        
        try:
            review_text = review_card.find("div", {"class": "review-content-body"}).text.strip()
            
        except Exception:
            review_text = ""

        try:
            review_date = review_card.find("span", {"class": "review-content__date"}).text.strip()
            review_date = datetime.strptime(review_date, '%b %d, %Y')
        except Exception:
            review_date = ""
        
        try:
            review_author = review_card.find("div", {"class": "review-content__no-padding col__12-12"}).find("button").text.strip()
        except Exception:
            review_author = ""
        
        try:
            original_review_syndication = review_card.find("div", {"class": "syndication-section col__12-12"}).text.strip()
        except Exception:
            original_review_syndication = ""
        
        try:
            review_recommended = review_card.find("div", {"class": "review-status-icons"}).find("span", {"class": "ratings-reviews__badge-text--full"}).text.strip()
        except Exception:
            review_recommended = ""

        try:
            verified_purchaser = review_card.find("li", {"class": "review-badge"}).text.strip()
            if "Verified Purchase" in verified_purchaser:
                verified_purchase_badge = "Verified Purchase"
            else:
                verified_purchase_badge = ""
        except Exception:
            verified_purchase_badge = ""

        try:
            image_list = []

            images = review_card.find_all("div", {"class": "media-carousel__media"})
            try:
                for image in images:
                    if 'url("' in image.find("button")["style"]:
                        image_list += [image.find("button")["style"].split('url("')[-1][:-3]]
                    else:
                        image_list += [image.find("button")["style"].split('url(')[-1][:-2]]
            except Exception:
                print("Couldnt get images", image)
        
        except Exception:
            image_list = []

        review_dictionary = {
            "Type": product_dictionary['Type'],
            "Store": "HomeDepot.com",
            "Manufacturer": product_dictionary['Manufacturer'],
            "Model No.": product_dictionary["Model No."],
            "Price $": product_dictionary['Price $'],
            "Model Description": product_dictionary['Model Description'],
            "sku": product_dictionary['sku'],
            "url": product_dictionary['url'],
            "product_image": product_dictionary['product_image'],
            "star_rating": star_rating,
            "review_title": review_title,
            "review_text": review_text,
            "review_date": review_date,
            "review_author": review_author,
            "original_review_syndication": original_review_syndication,
            "review_recommended": review_recommended, # Needs to match the styles of other TODO
            "verified_purchase_badge": verified_purchase_badge,
            "image_list": image_list
        }

        review_dictionary_list += [review_dictionary]

    print(review_dictionary_list)
    return review_dictionary_list

def get_reviews_worker(n, q):
    
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                print("Getting json...")
                get_reviews(data)
                print("Got json!")

                print("Great Success")
                q.task_done()
            except Exception:
                print("Couldn't get data from", data)
                q.task_done()
        except Exception:
            print("Thread", n, "has joined")
            break
        
def went_back_far_enough(review_dictionary_list, n_days_ago):
    
    # get rid of reviews without a review_date   
    for review_list in review_dictionary_list:
        review_list.reverse()
        
        for review in review_list:
            #print(review)
            if review["review_date"] != "":
                if review["review_date"] < n_days_ago:
                    return True
                
    return False

def get_reviews(product_dictionary, n_days_ago):
    
    url = product_dictionary["url"]
    print(url)
    global driver
    #driver = getDriver()
    driver.get(url)
    #scroll down to the specifications section
    driver.execute_script("window.scrollTo(0, 900)")
    #click on the specifications tab
    sleep(1.5)

    try:
        sort_reviews_tab = Select(driver.find_element(By.XPATH, '//*[@class="drop-down__select"]'))
        sort_reviews_tab.select_by_value("newest")
        #input("adjust filters and press enter")
    except Exception as e:
        print(e)
        print("Product has no reviews")

    sleep(2)

    review_dictionary_list = []
    review_set = set()
    while True:
        
        if review_dictionary_list != []:
            if went_back_far_enough(review_dictionary_list, n_days_ago):
                break
        
        try:
            
            # get new reviews
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            new_reviews = parse_reviews(soup, product_dictionary)
            print("___")
            print("|", len(new_reviews), "|")
            print("___")
            review_dictionary_list += [new_reviews]
            
            len_old_review = len(review_set)
            print(len_old_review)
            for review in new_reviews:
                review_set.add(review["review_text"])
            len_new_review = len(review_set)
            print(len_new_review, len_old_review)
            if len_old_review == len_new_review:
                break
            
            # click the next link
            for i in range(6):
                try:
                    
                    try:
                        sleep(2)
                        next_page_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                        print(next_page_button)
                        next_page_button.click()
                        sleep(1)
                        driver.execute_script("window.scrollBy(0, 1500)")
                        sleep(1)
                        driver.execute_script("window.scrollBy(0, 1500)")
                        
                    except Exception as e:
                        next_page_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
                        print(next_page_button)
                        next_page_button.click()
                        sleep(1)
                        driver.execute_script("window.scrollBy(0, 1500)")
                        sleep(1)
                        driver.execute_script("window.scrollBy(0, 1500)")
                        
                    sleep(5)
                    
                    break
                except Exception as e:
                    print(i, e)
                    # scroll down a little
                    driver.execute_script("window.scrollBy(0, 1500)")
                    sleep(4)
            
        except Exception as e:
            print(e)
            print("No more pages")
            break
    
    return review_dictionary_list
    
def parse_products(html):

    product_dictionaries_to_return = []
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.find_all("div", {"data-testid": "product-pod"})
    for product in products:
        try:
            manufacturer = product.find("p", {"class": "product-header__title__brand--bold--ey0fs"}).text.strip()
        except Exception as e:
            manufacturer = ""
            print(e)
        
        try:
            model_number = product.find("div", {"style": "min-height:21px"}).text.strip()
            try:
                print(model_number)
                model_number = model_number.replace("Model#", "").replace("Model #", "").strip()
                print(model_number)
            except Exception as e:
                model_number = ""
                print(e)
                
        except Exception as e:
            model_number = ""
            print(e)
        
        try:
            price_list = product.find("div", {"class": "price"}).find_all("span")
            price = price_list[0].text.strip() + price_list[1].text.strip() + price_list[2].text.strip() + price_list[3].text.strip()

            
        except Exception as e:
            price = ""
            print(e)


        # going to start scraping product images
        try:
            product_image = product.find("img")['src'] # changing this to img, will pickup the first image src in ("div", {"data-testid": "product-pod"})
        except Exception as e:
            product_image = ""
            print(e)
            
            
        try:
            model_description = product.find("span", {"class": "sui-text-primary sui-font-regular sui-mb-1 sui-line-clamp-5 sui-text-ellipsis sui-inline"}).text.strip()
        except Exception as e:
            model_description = ""
            print(e)
        
        
        try:
            url = product.find("a")["href"]
        except Exception as e:
            url = ""
            print(e)

        global appliance_type_global
        product_dictionary = {
            "Type": appliance_type_global,
            "Store": "Homedepot.com",
            "Manufacturer": manufacturer,
            "Model No.": model_number,
            "Price $": price,
            "Model Description": model_description,
            #"sku": product_dictionary["sku"],          #potential reason for Home Depot reviews failing
            "url": "https://www.homedepot.com" + url,
            "product_image": product_image
        }
        print(product_dictionary)
        product_dictionaries_to_return += [product_dictionary]
    
    return product_dictionaries_to_return
            

appliance_type_global = ""
product_dictionary_q = Queue(maxsize=0)
driver = ""
def main(appliance_type, n_days_ago, number_of_pages, start_url):
    
    global appliance_type_global
    appliance_type_global = appliance_type
    global driver
    driver = getDriver()

    driver.get(start_url)
    
    
    product_dictionaries_to_scrape = []

    
    for i in range(number_of_pages):
        
        try:
            # scroll to bottom of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(10)
            html = driver.page_source
            products_from_page = parse_products(html)
            # find element by aria label
            
            # if number_of_pages > 1:
            #     next_page_button = driver.find_element(By.XPATH, '//*[@aria-label="Next"]')
            #     next_page_button.click()

            try: 
                if number_of_pages > 1: 
                    retries = 0
                    while True:
                        try:
                            if retries > 5:
                                break
                            next_page_button = driver.find_element(By.XPATH, '//*[@aria-label="Next"]') 
                            next_page_button.click()
                            break
                        except Exception as e:
                            print(e)
                            # scroll up a little
                            driver.execute_script("window.scrollBy(0, -300)")
                            sleep(1)
                            retries += 1
  
                sleep(3) 
                product_dictionaries_to_scrape += products_from_page  
            
            except Exception as e:
                product_dictionaries_to_scrape += products_from_page
                print(e)
        
        except Exception as e:
                print(e)
            
    starting_dataframe= pd.DataFrame(product_dictionaries_to_scrape)
    
    # drop the duplicates
    starting_dataframe.drop_duplicates(inplace=True)
    starting_dataframe.to_excel("outputs/Product Lists/" + "Homedepot.com "+ appliance_type + " Products " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    
    product_dictionaries_to_scrape = []
    for index, row in starting_dataframe.iterrows():
        product_dictionary = row.to_dict()
        product_dictionary["url"] = product_dictionary["url"].split("/p/")[0] + "/p/" + "reviews/" + product_dictionary["url"].split("/p/")[1]
        product_dictionaries_to_scrape += [product_dictionary]
        

    # remove duplicate product dictionaries
    product_dictionaries_to_scrape = list({v['url']:v for v in product_dictionaries_to_scrape}.values())

    review_dictionary_list = []
    for product_dictionary in tqdm(product_dictionaries_to_scrape, total=len(product_dictionaries_to_scrape)):
        
        while True:
            retries = 0
            try:
                if retries > 5:
                    my_reviews = []
                    break
                my_reviews = get_reviews(product_dictionary, n_days_ago)
                break
            except Exception as e:
                driver = getDriver()
                print(e)
                retries += 1
        
        for my_list in my_reviews:
            for my_dict in my_list:
                review_dictionary_list += [my_dict]
    
    print(review_dictionary_list)
    print(len(review_dictionary_list))
    dataframe_to_export = pd.DataFrame(review_dictionary_list)
    dataframe_to_export.to_excel("outputs/Reviews/" + "Homedepot " + appliance_type + " Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)



#just for testing purpose
if __name__ == '__main__':
    # pick up here with new variables in main
    days_back = input("Enter the number of days back you want to scrape: ")
    n_days_ago = datetime.now() - timedelta(days=int(days_back))
    main("Dehumidifier", n_days_ago, 1, "https://www.homedepot.com/b/Heating-Venting-Cooling-Dehumidifiers/N-5yc1vZc4l8")
    
   
    