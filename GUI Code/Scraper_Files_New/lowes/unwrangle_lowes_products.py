import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from Scraper_Files_New.lowes import s3_read_and_write
import itertools

PRODUCT_DESTINATION_KEY = 'raw-scraping-outputs/lowes/products/' + str(datetime.now()) + '.csv'

def get_products_df(SEARCH_TERM, API_KEY):
    
    BASE_URL = 'https://data.unwrangle.com/api/getter/?platform=lowes_search&search=' + SEARCH_TERM + '&api_key='
    
    # initialize variables
    products_list = []
    page_number = 1
    product_set = set()
    previous_set_length = 0

    while True:

        url = f"{BASE_URL}{API_KEY}&page={page_number}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if 'results' in data and isinstance(data['results'], list):

                # append the results to the products list
                for item in data['results']:
                    products_list.append(item)
                    product_set.add(item['url'])
                
                # if nothing new was added to the set, break
                if len(product_set) == previous_set_length:
                    print("No new products found")
                    break
                else:            
                    print(f"Page {page_number} done")
                    previous_set_length = len(product_set)
                    page_number += 1
                    

        
                    
    # Convert to DataFrame
    products_df = pd.DataFrame(products_list)
    products_df.drop_duplicates(subset="url", inplace=True)
    # print all col names
    print(products_df.columns)
    products_df.to_csv('lowes_product_search_response_df.csv')
    return products_df

# Function to fetch product data
def fetch_product_data(product_url, API_KEY):
    """Fetch product details from API"""
    url = f"https://data.unwrangle.com/api/getter/?platform=lowes_detail&url={product_url}&api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            return {'url': product_url, **response.json()['detail']}  # Flatten JSON & keep URL
        except (KeyError, ValueError):
            return {'url': product_url, 'error': 'Invalid JSON'}
    else:
        return {'url': product_url, 'error': f"HTTP {response.status_code}"}

# Use ThreadPoolExecutor for multithreading

def main(SEARCH_TERM, API_KEY, DESTINATION_BUCKET):
    product_data_list = []
    
    products_df = get_products_df(SEARCH_TERM, API_KEY)
    print(products_df)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_product_data, products_df['url'], itertools.repeat(API_KEY)))
        product_data_list.extend(results)

    # Convert results to DataFrame
    product_data_df = pd.DataFrame(product_data_list)


    # Merge with original DataFrame
    df_merged = products_df.merge(product_data_df, on="url", how="left")

    # Save merged results
    s3_read_and_write.save_csv_to_s3(bucket_name=DESTINATION_BUCKET, s3_key=PRODUCT_DESTINATION_KEY, df=df_merged)
    return df_merged