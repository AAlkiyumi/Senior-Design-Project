import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import concurrent.futures
import s3_read_and_write
import itertools


REVIEW_DESTINATION_KEY = 'raw-scraping-outputs/homedepot/reviews/' + str(datetime.now()) + '.csv'
BASE_URL = "https://data.unwrangle.com/api/getter/"

def get_review(product_url, API_KEY, CUTOFF_DATE):

    reviews_dictionary_list = []
    
    # Subtract 7 days from today's date
    page_number = 1
    retries = 0
    max_pages = 1000
    while True:
        
        if (retries > 2) or (page_number > max_pages):
            break
        
        # call the api
        params = {
            "url": product_url,
            "page": page_number,
            "platform": "homedepot_reviews",
            "api_key": API_KEY
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            
            # convert the response to a dictionary
            response_dictionary = json.loads(response.text)
            
            if page_number == 1:
                max_pages = response_dictionary['no_of_pages']
            
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
    


# Function to fetch reviews (wraps get_review)
def fetch_review_data(product_url, API_KEY, CUTOFF_DATE):
    """Fetch reviews for a product and cross join with product details"""
    try:
        return get_review(product_url, API_KEY, CUTOFF_DATE)  # get_review() is assumed to return a DataFrame
    except Exception as e:
        print(f"Error fetching reviews for {product_url}: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs

def main(product_df, DAYS_AGO, API_KEY, DESTINATION_BUCKET):

    today = datetime.today().date()
    CUTOFF_DATE = today - timedelta(DAYS_AGO)
    df = product_df
    
    df.drop_duplicates(subset='id', inplace=True)
    # Use ThreadPoolExecutor for multithreading
    review_data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_review_data, df['url_x'], itertools.repeat(API_KEY), itertools.repeat(CUTOFF_DATE)))
        review_data_list.extend(results)
        
    
    # get the lists of lists of dictionaries into a single list of dictionaries
    review_dictionary_list = []
    for mylist in review_data_list:
        for sublist in mylist:
            for dictionary in sublist:
                review_dictionary_list.append(dictionary)
    
    reviews_df = pd.DataFrame(review_dictionary_list)
    
    # drop any reviews older than 7 days
    reviews_df['date'] = pd.to_datetime(reviews_df['date'])
    reviews_df = reviews_df[reviews_df['date'] >= pd.to_datetime(CUTOFF_DATE)]
    
    s3_read_and_write.save_csv_to_s3(bucket_name=DESTINATION_BUCKET, s3_key=REVIEW_DESTINATION_KEY, df=reviews_df)