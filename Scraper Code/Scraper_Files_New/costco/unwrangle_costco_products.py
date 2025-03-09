import requests
import pandas as pd
import json 
import s3_read_and_write
from datetime import datetime
# These are the only things you need to change
####################################################################

####################################################################


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

    return response_df
