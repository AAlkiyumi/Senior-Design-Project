import requests
import pandas as pd
import json
import concurrent.futures
from datetime import datetime
from Scraper_Files_New.walmart import s3_read_and_write
import itertools

PRODUCTS_DESTINATION_KEY = 'raw-scraping-outputs/walmart/products/' + str(datetime.now()) + '.csv'

def search_products(SEARCH_TERM, API_KEY):
    search_id_set = set()
    response_dictionary_list = []
    # make 1 call to the unwranlge api for each page number
    for page_number in range(101):
        print('On Page: ' + str(page_number))
        
        # call the api
        url = 'https://data.unwrangle.com/api/getter/?platform=walmart_search&search=' + str(SEARCH_TERM) + '&page=' + str(page_number+1) + '&api_key=' + str(API_KEY)
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # convert the response to a dictionary and append to the list
            response_dictionary = json.loads(response.text)['results']
            if len(response_dictionary) == 0:
                print('Breaking')
                break
            
            if response_dictionary[-1]['id'] in search_id_set:
                for result in response_dictionary:
                    search_id_set.add(result['id'])
                    
                print('repeat found')
                break
            else:
                for result in response_dictionary:
                    search_id_set.add(result['id'])
                    #print(result['id'])

            response_dictionary_list.append(response_dictionary)
        
            
        except requests.exceptions.RequestException as e:
            print(f"Error on page {page_number}: {e}")
            break  # Optionally break if an error occurs, or handle differently
            # convert the results to a list of dictionaries and append it to the entire list
        

    # convert the lists to dataframes
    response_df = pd.DataFrame([item for sublist in response_dictionary_list for item in sublist])

    # save the dataframes to csv files
    response_df.to_csv('walmart_product_search_response_df.csv')
    return response_df

BASE_URL = 'https://data.unwrangle.com/api/getter/?platform=walmart_detail&url='


# Function to fetch product data
def fetch_product_data(product_url, API_KEY):
    """Fetch product details from API"""
    try:
        url = f"{BASE_URL}{product_url}&api_key={API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            try:
                return {'url': product_url, **response.json()['detail']}  # Keep URL for merging
            except (KeyError, ValueError, json.JSONDecodeError):
                return {'url': product_url, 'error': 'Invalid JSON'}
        else:
            return {'url': product_url, 'error': f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {'url': product_url, 'error': str(e)}

# Function to get product data using multithreading
def get_product_data(df, API_KEY, max_workers=50):
    """Fetch product data concurrently using multithreading"""
    num_rows = len(df)
    details_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fetch_product_data, df['url'], itertools.repeat(API_KEY)))
        details_list.extend(results)

    # Convert results to DataFrame
    details_df = pd.DataFrame(details_list)
    

    # Merge with original DataFrame
    return details_df

            
def main(SEARCH_TERM, API_KEY, DESTINATION_BUCKET):
    products_df = search_products(SEARCH_TERM, API_KEY)
    
    
    product_data = get_product_data(products_df, API_KEY)
    #product_data.to_csv('walmart_product_data.csv', index=False)
    
    
    # typecast the id column to a string
    products_df['id'] = products_df['id'].astype(str)
    product_data['id'] = product_data['id'].astype(str)
    
    products_merged_df = products_df.merge(product_data, on="id", how="left")
    products_merged_df.drop_duplicates(subset="id", inplace=True)
    
    s3_read_and_write.save_csv_to_s3(bucket_name=DESTINATION_BUCKET, s3_key=PRODUCTS_DESTINATION_KEY, df=products_merged_df)
    return products_merged_df