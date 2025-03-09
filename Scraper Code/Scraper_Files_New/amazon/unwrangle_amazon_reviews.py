import requests
from datetime import datetime, timedelta
import json
import pandas as pd
import concurrent.futures
import s3_read_and_write
from datetime import datetime
import itertools


REVIEW_DESTINATION_KEY = 'raw-scraping-outputs/amazon/reviews/' + str(datetime.now()) + '.csv'
BASE_URL = 'https://data.unwrangle.com/api/getter/'



def fetch_review_data(asin, API_KEY, COOKIE, CUTOFF_DATE):
    """
    Fetch a single page of reviews for a product.
    """
    
    reviews_dictionary_list = []
    page_number = 1
    retries = 0
    while (page_number < 11) and (retries < 2):
            
        params = {
            'asin': asin,
            'country_code': 'us',
            'platform': 'amazon_reviews',
            'sort_by': 'recent',
            'api_key': API_KEY,
            'cookie': COOKIE,
            'page': page_number,
        }
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            
            reviews_dictionary_results_list = json.loads(response.text)["reviews"]
            for dictionary in reviews_dictionary_results_list:
                dictionary['asin'] = asin
        
            reviews_dictionary_list.append(reviews_dictionary_results_list)
            
            if len(reviews_dictionary_results_list) == 0:
                print(f"No results found on page {page_number}, stopping.")
                break
            
            last_review_date_str = reviews_dictionary_results_list[-1]['date']
            last_review_date = datetime.strptime(last_review_date_str, '%Y-%m-%d').date()
            
            if last_review_date < CUTOFF_DATE:
                print(f"Last review date {last_review_date} is older than 7 days, stopping.")
                break  # Exit the loop early if condition is met
            page_number += 1
            
        else:
            print(f"Error: Received status code {response.status_code} when fetching reviews")
            print(f"Response content: {response.text}")
            retries += 1


    return reviews_dictionary_list



def main(product_df, API_KEY, DESTINATION_BUCKET, DAYS_AGO, COOKIE):
    
    TODAY = datetime.today().date()
    CUTOFF_DATE = TODAY - timedelta(DAYS_AGO)

    df = product_df
    df.drop_duplicates(subset='asin', inplace=True)
    
    # Use ThreadPoolExecutor for multithreading
    review_data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_review_data, df['asin'], itertools.repeat(API_KEY), itertools.repeat(COOKIE), itertools.repeat(CUTOFF_DATE)))
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