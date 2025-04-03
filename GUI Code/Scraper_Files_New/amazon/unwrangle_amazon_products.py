import requests
import pandas as pd
import concurrent.futures
import json
from Scraper_Files_New.amazon import s3_read_and_write
from datetime import datetime


PRODUCT_DESTINATION_KEY = 'raw-scraping-outputs/amazon/products/' + str(datetime.now()) + '.csv'
BASE_URL = 'https://data.unwrangle.com/api/getter/'

def main(SEARCH_TERM, API_KEY, DESTINATION_BUCKET):
    #################################
    #     Get the products df       #
    #################################
    response_dictionary_list = []
    for page in range(1, 100):
        print(page)
        params = {
            'platform': 'amazon_search',
            'search': SEARCH_TERM,
            'page': page,
            'country_code': 'us',
            'api_key': API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        
        # if the page number is greater than the number of pages, break
        if page > int(response.json()['no_of_pages']):
            break
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "results" in data:
                response_dictionary_results_list = json.loads(response.text)["results"]
                response_dictionary_list.append(response_dictionary_results_list)
            else:
                print(f"No successful results on page {page}.")
        else:
            print(f"Failed to fetch data for page {page} (Status code: {response.status_code}).")
            
        

    products_df = pd.DataFrame([item for sublist in response_dictionary_list for item in sublist])
    products_df.drop_duplicates(subset="asin", inplace=True)
    products_df.to_csv('amazon_product_search_response_df.csv')


    def fetch_product_data(asin, country_code='us'):
        
        url = 'https://data.unwrangle.com/api/getter/?platform=amazon_detail&asin=' + str(asin) + '&country_code=' + str(country_code) + '&api_key=' + str(API_KEY)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            try:
                return {'asin': asin, **response.json()['detail']}  # Flatten JSON & keep asin
            except (KeyError, ValueError):
                return {'url': asin, 'error': 'Invalid JSON'}
        else:
            return {'url': asin, 'error': f"HTTP {response.status_code}"}
        

    # Use ThreadPoolExecutor for multithreading
    product_data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_product_data, products_df['asin']))
        product_data_list.extend(results)

    # convert the results to a df
    product_data_df = pd.DataFrame(product_data_list)

    # merge with the products df
    df_merged = pd.merge(products_df, product_data_df, on='asin', how='left')

    s3_read_and_write.save_csv_to_s3(bucket_name=DESTINATION_BUCKET, s3_key=PRODUCT_DESTINATION_KEY, df=df_merged)

    return df_merged
