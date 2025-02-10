import requests
import pandas as pd
import json
import api_keys

API_KEY = api_keys.get_unwrangle_API_key()


def unwrangle_walmart_product_data(product_url_list):
    
    response_dictionary_list = []
    details_dictionary_list = []
    for product_url in product_url_list:
        # call the api
        url = 'https://data.unwrangle.com/api/getter/?platform=walmart_detail&url=' + product_url + '&api_key=' + str(API_KEY)
        response = requests.get(url)
        
        # convert the response to a dictionary
        response_dictionary = json.loads(response.text) 
        details_dictionary = response_dictionary['detail']
        
        response_dictionary_list.append(response_dictionary)
        details_dictionary_list.append(details_dictionary)
        
    # convert dictionaries to dataframes
    response_df = pd.DataFrame(response_dictionary_list)
    details_df = pd.DataFrame(details_dictionary_list)
    
    # save the dataframes to csv files
    response_df.to_csv('walmart_product_data_response_df.csv')
    details_df.to_csv('walmart_product_data_details_df.csv')
    
    # return the dataframes to whatever called this function
    return response_df, details_df
        
        
# example call to product data
product_url_list = ["https://www.walmart.com/ip/Midea-5-000-BTU-150-Sq-ft-Mechanical-Window-Air-Conditioner-White-MAW05M1WWT/212092810?classType=VARIANT&athbdg=L1103"]
unwrangle_walmart_product_data(product_url_list)