import requests
import pandas as pd
import json 
import concurrent.futures
from Scraper_Files_New.costco import s3_read_and_write
from datetime import datetime
import itertools
# These are the only things you need to change
####################################################################

####################################################################

PRODUCT_DESTINATION_KEY = 'raw-scraping-outputs/costco/products/' + str(datetime.now()) + '.csv'
BASE_URL = 'https://data.unwrangle.com/api/getter/'

def get_products_df(SEARCH_TERM, API_KEY):
    response_dictionary_list = []

    
    page_number = 1
    max_pages = 1000
    retries = 0
    # Loop through pages 1 to 1000
    while (page_number < max_pages) and (retries < 2):
        url = f'https://data.unwrangle.com/api/getter/?platform=costco_search&search={SEARCH_TERM}&api_key={API_KEY}'
        
        
        try:
            response = requests.get(url)
            # Ensure the request was successful
            response.raise_for_status()
            
            if page_number == 1:
                max_pages = json.loads(response.text)["no_of_pages"]
            
            
            response_dictionary_results_list = json.loads(response.text)["results"]
            
            # Append the results from this page to the overall list
            response_dictionary_list.append(response_dictionary_results_list)
            
            # Break the loop if no results are returned (empty page)
            if len(response_dictionary_results_list) == 0:
                print(f"No results found on page {page_number}, stopping.")
                break
        
            page_number += 1
            retries = 0
                
        except requests.exceptions.RequestException as e:
            print(f"Error on page {page_number}: {e}")
            retries += 1
            

    # Convert the gathered data to a DataFrame
    response_df = pd.DataFrame([item for sublist in response_dictionary_list for item in sublist])
    # Save the results to a CSV file
    response_df.to_csv('costco_product_search_response_df.csv')

    return response_df

# Function to fetch product data
def fetch_product_data(product_id, API_KEY):
    """Fetch product details from API"""
    
    params = {
        'item_id': product_id,
        'platform': 'costco_detail',
        'api_key': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        try:
            return {'id': product_id, **response.json()['detail']}  # Flatten JSON & keep URL
        except (KeyError, ValueError):
            return {'id': product_id, 'error': 'Invalid JSON'}
    else:
        return {'url': product_id, 'error': f"HTTP {response.status_code}"}

def main(SEARCH_TERM, API_KEY, DESTINATION_BUCKET):
    products_df = get_products_df(SEARCH_TERM, API_KEY)
    products_df.drop_duplicates(subset='id', inplace=True)
    
    
    # Use ThreadPoolExecutor for multithreading
    product_data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_product_data, products_df['id'], itertools.repeat(API_KEY)))
        product_data_list.extend(results)

    # Convert results to DataFrame
    product_data_df = pd.DataFrame(product_data_list)
    
    
    # Merge the two DataFrames
    merged_df = pd.merge(products_df, product_data_df, on='id', how='left')
    
    s3_read_and_write.save_csv_to_s3(bucket_name=DESTINATION_BUCKET, s3_key=PRODUCT_DESTINATION_KEY, df=merged_df)
    return merged_df
    