import requests
import json
import pandas as pd
import api_keys

API_KEY = api_keys.get_unwrangle_API_key()

# function accepts a search term and a page number
# returns 2 dataframes, one with the response and one with the results
# exports the dataframes to csv files as well
def unwrangle_walmart_product_search(search_term, number_of_pages=1):
    
    # create empty lists to hold the dictionaries
    response_dictionary_list = []
    results_dictionary_list = []
    
    # make 1 call to the unwranlge api for each page number
    for page_number in range(number_of_pages):
        # call the api
        url = 'https://data.unwrangle.com/api/getter/?platform=walmart_search&search=' + str(search_term) + '&page=' + str(page_number+1) + '&api_key=' + str(API_KEY)
        response = requests.get(url)
        
        
        # convert the response to a dictionary and append to the list
        response_dictionary = json.loads(response.text)
        response_dictionary_list.append(response_dictionary)
        
        # convert the results to a list of dictionaries and append it to the entire list
        results_dictionary_list = response_dictionary['results']
        results_dictionary_list += results_dictionary_list
        
    
    # convert the lists to dataframes
    response_df = pd.DataFrame(response_dictionary_list)
    results_dictionary_df = pd.DataFrame(results_dictionary_list)
    print(results_dictionary_df.head())
    
    # save the dataframes to csv files
    response_df.to_csv('walmart_product_search_response_df.csv')
    results_dictionary_df.to_csv('walmart_product_search_results_df.csv')
    
    # return the dataframes to whatever called this function
    return response_df, results_dictionary_df




# example call to product search
unwrangle_walmart_product_search(search_term="window air conditioner", number_of_pages=1)


