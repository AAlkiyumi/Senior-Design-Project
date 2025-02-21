import pandas as pd
from tqdm import tqdm
from datetime import datetime

from queue import Queue
from threading import Thread

# load the two dataframes

print("Loading reviews data")
reviews_df = pd.read_excel("outputs/sentiment_outputs/WindowAC Tags and Sentiment Predictions 2024_4_24.xlsx", sheet_name="Reviews")
print("Loading sentences data")
sentences_df = pd.read_excel("outputs/sentiment_outputs/WindowAC Tags and Sentiment Predictions 2024_4_24.xlsx", sheet_name="Sentences")
output_file = "outputs/sentiment_outputs/" + "WindowAC custom sentiment " +  str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx"


def main(reviews_df, sentences_df_original):
    
    # go through the column headers of sentences_df 
    
    global topic_list
    topic_list = []
    for column in sentences_df.columns:
        
        if ("Predicted" in column) and ("Sentiment" in column):
            
            base_new_column = column.split("Predicted ")[1].split(" Sentiment")[0]
            
            positive_column = "Proportion of Sentences Positively Mentioning " + base_new_column
            neutral_column = "Proportion of Sentences Neutrally Mentioning " + base_new_column
            negative_column = "Proportion of Sentences Negatively Mentioning " + base_new_column
            
            # make sure these cols are double
        
            
            reviews_df[positive_column] = 0.0
            reviews_df[neutral_column] = 0.0
            reviews_df[negative_column] = 0.0
            
            topic_list.append(base_new_column)
    
            
    
    hashmap = {}
    # this can be multi-threaded
    print("Calculating proportions")
    for index, row in tqdm(sentences_df.iterrows(), total=sentences_df.shape[0]):
        
        for topic in topic_list:
            try:
                if row["Predicted " + topic + " Sentiment"] == "POSITIVE":
                    hashmap[row["Key"]][topic]["POSITIVE"] += 1
            except:
                try:
                    hashmap[row["Key"]][topic] = {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": 0}
                except:
                    hashmap[row["Key"]] = {topic: {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": 0}}
            
            try:
                if row["Predicted " + topic + " Sentiment"] == "NEUTRAL":
                    hashmap[row["Key"]][topic]["NEUTRAL"] += 1
            except:
                try:
                    hashmap[row["Key"]][topic] = {"POSITIVE": 0, "NEUTRAL": 1, "NEGATIVE": 0}
                except:
                    hashmap[row["Key"]] = {topic: {"POSITIVE": 0, "NEUTRAL": 1, "NEGATIVE": 0}}
                
            try:
                if row["Predicted " + topic + " Sentiment"] == "NEGATIVE":
                    hashmap[row["Key"]][topic]["NEGATIVE"] += 1
            except:
                try:
                    hashmap[row["Key"]][topic] = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 1}
                except:
                    hashmap[row["Key"]] = {topic: {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 1}}
    
    #print(hashmap)
    
    for whole_key, whole_value in tqdm(hashmap.items(), total=len(hashmap)):
        
        for topic_key, topic_value in whole_value.items():
            positive = topic_value["POSITIVE"]
            neutral = topic_value["NEUTRAL"]
            negative = topic_value["NEGATIVE"]
            
            denominator = positive + neutral + negative
            
            if denominator != 0:
                hashmap[whole_key][topic_key]["Proportion Positive"] = positive / denominator
                hashmap[whole_key][topic_key]["Proportion Neutral"] = neutral / denominator
                hashmap[whole_key][topic_key]["Proportion Negative"] = negative / denominator
                hashmap[whole_key][topic_key]["Proportion Total"] = denominator

            #print(hashmap[whole_key][topic_key])
            
    
    
    # now I need to append all this to the unpivoted df
    
    unpivoted_review_dict_list = []
    for index, row in tqdm(reviews_df.iterrows(), total=reviews_df.shape[0]):
        
        # turn row into a dict but only keep cetain columns
        # "Key", "Promoted Review", "product_image", "Amazon.com", "BestBuy.com", "Costco.com", "HomeDepot.com", "Lowes.com", "Walmart.com", "HomeDepot.ca", "Lowes.ca", "Walmart.ca", "HomeHardware.ca", "Rona.ca", "CanadianTire.ca", "review_date", "star_rating", "Brand", "Model No.", "Price"
        temp_dict = {
            "Key": row["Key"],
            "Promoted Review": row["Promoted Review"],
            "product_image": row["product_image"],
            "Amazon.com": row["Amazon.com"],
            "BestBuy.com": row["BestBuy.com"],
            "Costco.com": row["Costco.com"],
            "HomeDepot.com": row["HomeDepot.com"],
            "Lowes.com": row["Lowes.com"],
            "Walmart.com": row["Walmart.com"],
            "HomeDepot.ca": row["HomeDepot.ca"],
            "Lowes.ca": row["Lowes.ca"],
            "Walmart.ca": row["Walmart.ca"],
            "HomeHardware.ca": row["HomeHardware.ca"],
            "Rona.ca": row["Rona.ca"],
            "CanadianTire.ca": row["CanadianTire.ca"],
            "review_date": row["review_date"],
            "star_rating": row["star_rating"],
            "Brand": row["Brand"],
            "Model No.": row["Model No."],
            "Price": row["Price"]
        }
        
        if row["Key"] in hashmap:
            for topic_key, topic_value in hashmap[row["Key"]].items():
                if topic_value["Proportion Total"] != 0:
                    
                    temp_dict["Topic"] = topic_key
                    temp_dict["Proportion Negative"] = topic_value["Proportion Negative"]
                    temp_dict["Proportion Neutral"] = topic_value["Proportion Neutral"]
                    temp_dict["Proportion Positive"] = topic_value["Proportion Positive"]
                    
                    unpivoted_review_dict_list.append(temp_dict)
                
    unpivoted_review_df = pd.DataFrame(unpivoted_review_dict_list)
    unpivoted_review_df["review_date"] = unpivoted_review_df["review_date"].dt.strftime('%Y-%m-%d')
    unpivoted_review_df = unpivoted_review_df.drop_duplicates()
    unpivoted_review_df.to_csv("outputs/sentiment_outputs/unpivoted reviews.csv", index=False)
            
    
    unpivoted_sentence_dict_list = []
    for index, row in tqdm(sentences_df_original.iterrows(), total=sentences_df_original.shape[0]):
        for topic in topic_list:
            if row[topic]:
                temp_dict = {
                    "product_image": row["product_image"],
                    "review_date": row["review_date"],
                    "Topic": topic,
                    "Topic Sentiment": row["Predicted " + topic + " Sentiment"],
                    "sentence": row["sentence"],
                    "review_title": row["review_title"],
                    "review_text": row["review_text"],
                    "star_rating": row["star_rating"],
                    "Promoted Review": row["Promoted Review"],
                    "original_review_syndication": row["original_review_syndication"],
                    "Amazon.com": row["Amazon.com"],
                    "BestBuy.com": row["BestBuy.com"],
                    "Costco.com": row["Costco.com"],
                    "HomeDepot.com": row["HomeDepot.com"],
                    "Lowes.com": row["Lowes.com"],
                    "Walmart.com": row["Walmart.com"],
                    "HomeDepot.ca": row["HomeDepot.ca"],
                    "Lowes.ca": row["Lowes.ca"],
                    "Walmart.ca": row["Walmart.ca"],
                    "HomeHardware.ca": row["HomeHardware.ca"],
                    "Rona.ca": row["Rona.ca"],
                    "CanadianTire.ca": row["CanadianTire.ca"],
                    "Brand": row["Brand"],
                    "Model No.": row["Model No."],
                    "Model Description": row["Model Description"],
                    "Price": row["Price"],
                    "url_list": row["url_list"],
                    "recommended": row["recommended"],
                    "sku": row["sku"],
                    "image_list": row["image_list"],
                    "Key": row["Key"]   
                }
                unpivoted_sentence_dict_list.append(temp_dict)
    
    unpivoted_sentence_df = pd.DataFrame(unpivoted_sentence_dict_list)
    unpivoted_sentence_df["review_date"] = unpivoted_sentence_df["review_date"].dt.strftime('%Y-%m-%d')
    unpivoted_sentence_df = unpivoted_sentence_df.drop_duplicates()
    
    # for the review_date col change format to yyyy-mm-dd no time
    unpivoted_sentence_df.to_csv("outputs/sentiment_outputs/unpivoted sentences.csv", index=False)
    

if __name__ == "__main__":
    main(reviews_df, sentences_df)    
    
    
