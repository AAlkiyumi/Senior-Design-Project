import requests
import pandas as pd
import json
import api_keys

API_KEY = api_keys.get_unwrangle_API_key()


def unwrangle_walmart_product_reviews(product_url_list, number_of_pages=1):
    
    response_dictionary_list = []
    reviews_dictionary_list = []
    for product_url in product_url_list:
        
        review_id_set = set()
        reviews_dictionary_list = []
        for page_number in range(number_of_pages):
            # call the api
            url = 'https://data.unwrangle.com/api/getter/?url=' + product_url + '&page=' + str(page_number+1) + '&platform=walmart_reviews&api_key=' + str(API_KEY)
            response = requests.get(url)
            
            # convert the response to a dictionary
            response_dictionary = json.loads(response.text)
            temp_reviews_dictionary_list = response_dictionary['reviews']
            
            if len(temp_reviews_dictionary_list) == 0:
                break
            
            if temp_reviews_dictionary_list[-1]['id'] in review_id_set:
                break
            else:
                for review in reviews_dictionary_list:
                    review_id_set.add(review['id'])
                    
            # append the dictionaries to the running lists
            response_dictionary_list.append(response_dictionary)
            reviews_dictionary_list += temp_reviews_dictionary_list
            
            
            

            
    
    # convert the lists to dataframes
    response_df = pd.DataFrame(response_dictionary_list)
    reviews_df = pd.DataFrame(reviews_dictionary_list)
    
    # save the dataframes to csv files
    response_df.to_csv('walmart_product_reviews_response_df.csv')
    reviews_df.to_csv('walmart_product_reviews_reviews_df.csv')
    
    # return the dataframes to whatever called this function
    return response_df, reviews_df
            
           
 
# product urls may need to be cleaned from step 1
product_url_list = ["https://www.walmart.com/ip/Midea-5-000-BTU-150-Sq-ft-Mechanical-Window-Air-Conditioner-White-MAW05M1WWT/212092810"]
unwrangle_walmart_product_reviews(product_url_list=product_url_list, number_of_pages=1000)