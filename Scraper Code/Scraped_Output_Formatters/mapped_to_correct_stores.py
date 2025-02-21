import pandas as pd
from tqdm import tqdm
import nltk

nltk.download("punkt")
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('wordnet')

def map_duped_reviews_to_shared_stores(df, list_of_stores, sentences_and_sentiment_scores_df=None):
    #list_of_stores = ["Amazon.com", "BestBuy.com", "Costco.com", "HomeDepot.com", "Lowes.com", "Walmart.com", "HomeDepot.ca", "Lowes.ca", "Walmart.ca", "HomeHardware.ca", "Rona.ca", "CanadianTire.ca"]
    
    # create new cols in the df to represent each of the stores
    for store in list_of_stores:
        df[store] = 0
    
    
    df["url_list"] = [[] for i in range(len(df))]

    # go through the data frame and mark the store the review is from as well as 
    # add the url to the url list
    for index, row in df.iterrows():
        df.at[index, row["Store"]] = 1
        
        df.at[index, "url_list"].append(row["url"])

    # now we need to look at all of the duplicated reviews and seperate them out:
    duplicated_reviews = df[df.duplicated(subset=["Key"], keep=False)]
    print(duplicated_reviews)
    # drop all duplicates
    df.drop_duplicates(subset=["Key"], keep=False, inplace=True)


    list_of_dictionaries_to_add = []
    # get set of all duplicated keys
    duplicated_keys = set(duplicated_reviews["Key"])

    for key in duplicated_keys:
        # narrow down to one set of duplicated at a time
        duplicated_review_subset = duplicated_reviews[duplicated_reviews["Key"] == key]
        
        
        if len(set(duplicated_review_subset["Store"].to_list())) == 1:
            print(set(duplicated_review_subset["Store"].to_list()))    
            # turn the first row of duplicated_review_subset into a dataframe
            new_row = duplicated_review_subset.iloc[0].to_dict()
            
            
        else:
            print(key)
            print(duplicated_review_subset["Store"].to_list())
            # print(duplicated_review_subset)
            # turn the first row of duplicated_review_subset into a dict
            new_row = duplicated_review_subset.iloc[0].to_dict()

            stores_to_add = set(duplicated_review_subset["Store"].to_list())
            for store in stores_to_add:
                new_row[store] = 1
            
            urls_to_add = set(duplicated_review_subset["url"].to_list())
            for url in urls_to_add:
                new_row["url_list"].append(url)

            
            
        new_row["url_list"] = str(list(set(new_row["url_list"])))
        list_of_dictionaries_to_add += [new_row]

    # add the list of dictionaries to df
    df = df._append(list_of_dictionaries_to_add, ignore_index=True)
    print(df.shape)
    print("_"*100)
    
    
    
    # now I need to double check that there are no more duplicates by checking the sentences
    print("Checking for additional duplicates")
    
    if sentences_and_sentiment_scores_df is None:
        row_list = []
        keys = []
        sentences_only = []
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            
            review_text = str(row['review_text'])
            indexes_to_add_space = []
            # if there is a puncuation mark not followed by a space, add a space
            for index in range(len(review_text)):
                if index + 1 != len(review_text):
                    if (review_text[index] in [".", "!", "?", ""]) and (review_text[index + 1] != " "):
                        
                        if review_text[index] != ".":
                            indexes_to_add_space.append(index + 1)
                            
                        else:
                            if review_text[index + 1] != ".":
                                indexes_to_add_space.append(index + 1)
                                
            for index in reversed(indexes_to_add_space):
                review_text = review_text[:index] + " " + review_text[index:]
            
            
            
            sentences = nltk.sent_tokenize(review_text)
            for sentence in sentences:
                keys += [row['Key']]
                sentences_only += [sentence]
                row_list.append(row.to_dict())
                
        # Pack the values into the sentence data frame
        sentences_and_sentiment_scores_df = pd.DataFrame(row_list)
        # find the location of the review_text col in the starting_df
        review_text_col_index = df.columns.get_loc("review_text")
        
        # add the sentences_only and lemmas to the starting_df at the location of the review_text col
        sentences_and_sentiment_scores_df.insert(loc=review_text_col_index+1, column="sentence", value=sentences_only)
    
    
    sentence_key_dict = {}
    
    
    for index, row in tqdm(sentences_and_sentiment_scores_df.iterrows(), total=sentences_and_sentiment_scores_df.shape[0]):
        
        sentence = str(row["sentence"])
        review_author = str(row["review_author"])
        row["review_date"] = pd.to_datetime(row["review_date"])
        month_year = str(row["review_date"].month) + "_" + str(row["review_date"].year)
        
        if (sentence != "") and (review_author != ""):
            sentence_key = sentence + review_author + month_year
            
            if not(sentence_key in sentence_key_dict.keys()):
                sentence_key_dict[sentence_key] = row["Key"]
            else:
                df.at[index, "Key"] = sentence_key_dict[sentence_key]
         
         
         
    # now we repeat step 1       
    duplicated_reviews = df[df.duplicated(subset=["Key"], keep=False)]
    print(duplicated_reviews)
    # drop all duplicates
    df.drop_duplicates(subset=["Key"], keep=False, inplace=True)
    
    
    list_of_dictionaries_to_add = []
    # get set of all duplicated keys
    duplicated_keys = set(duplicated_reviews["Key"])

    for key in tqdm(duplicated_keys, total=len(duplicated_keys)):
        # narrow down to one set of duplicated at a time
        duplicated_review_subset = duplicated_reviews[duplicated_reviews["Key"] == key]
        
        
        if len(set(duplicated_review_subset["Store"].to_list())) == 1:
            print(set(duplicated_review_subset["Store"].to_list()))    
            # turn the first row of duplicated_review_subset into a dataframe
            new_row = duplicated_review_subset.iloc[0].to_dict()
            
            
        else:
            print(key)
            print(duplicated_review_subset["Store"].to_list())
            # print(duplicated_review_subset)
            # turn the first row of duplicated_review_subset into a dict
            new_row = duplicated_review_subset.iloc[0].to_dict()

            stores_to_add = set(duplicated_review_subset["Store"].to_list())
            
            if type(stores_to_add) == str:
                for store in stores_to_add:
                    new_row[store] = 1
            
            urls_to_add = set(duplicated_review_subset["url"].to_list())
            for url in urls_to_add:
                if isinstance(new_row["url_list"], str):
                    new_row["url_list"] = [new_row["url_list"]]
                new_row["url_list"].append(url)

            
        try:
            new_row["url_list"] = str(list(set(new_row["url_list"])))
        except Exception as e:
            print(e)
        list_of_dictionaries_to_add += [new_row]

    # add the list of dictionaries to df
    df = df._append(list_of_dictionaries_to_add, ignore_index=True)
    print(df.shape)
    print("_"*100)
    
    return df
    