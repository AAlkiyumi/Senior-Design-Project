import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import concurrent.futures
import s3_read_and_write
import itertools


REVIEW_DESTINATION_KEY = 'raw-scraping-outputs/walmart/reviews/' + str(datetime.now()) + '.csv'

def get_review(product_url, API_KEY, CUTOFF_DATE):

    reviews_dictionary_list = []
    
    # Subtract 7 days from today's date
    page_number = 1
    retries = 0
    while True:
        
        if retries > 2:
            break
        
        # call the api
        url = 'https://data.unwrangle.com/api/getter/?url=' + product_url + '&page=' + str(page_number) + '&platform=walmart_reviews&api_key=' + str(API_KEY)
        
        try:
            response = requests.get(url)
            response.raise_for_status()

            # convert the response to a dictionary
            response_dictionary = json.loads(response.text)
            reviews_dictionary_result = response_dictionary['reviews']
            
            for dictionary in reviews_dictionary_result:
                dictionary['url'] = product_url
            
            
            # append the dictionaries to the running lists
            reviews_dictionary_list.append(reviews_dictionary_result)

            if len(reviews_dictionary_result) == 0:
                print(f"No results found on page {page_number}, stopping.")
                break

            last_review_date_str = reviews_dictionary_result[-1]['date']
            last_review_date = datetime.strptime(last_review_date_str, '%Y-%m-%d').date()

            if last_review_date < CUTOFF_DATE:
                # print(f"Last review date {last_review_date} is older than 7 days, stopping.")
                break  # Exit the loop early if condition is met
            
            page_number += 1
            retries = 0

        except requests.exceptions.RequestException as e:
            print(f"Error on page {page_number}: {e}")
            retries += 1

    return reviews_dictionary_list
    

