import pandas as pd
from tqdm import tqdm
from datetime import datetime

# load the two dataframes

reviews_df = pd.read_excel("outputs/sentiment_outputs/Electric Kettle Tags and Sentiment Predictions 2024_3_26.xlsx", sheet_name="Reviews")
sentences_df = pd.read_excel("outputs/sentiment_outputs/Electric Kettle Tags and Sentiment Predictions 2024_3_26.xlsx", sheet_name="Sentences")
output_file = "outputs/sentiment_outputs/" + "Electric Kettle custom sentiment " +  str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx"

def main(reviews_df, sentences_df, output_file):
    

    
    
    # go through the column headers of sentences_df 
    
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
    
            
            
    
    for index, row in tqdm(reviews_df.iterrows(), total=reviews_df.shape[0]):
        
        for topic in topic_list:

            column_to_count = "Predicted " + topic + " Sentiment"
            
            # count the number of positives in sentences_df with matching key
            
            positive_count = sentences_df[sentences_df["Key"] == row["Key"]][column_to_count].value_counts().get("POSITIVE", 0)
            neutral_count = sentences_df[sentences_df["Key"] == row["Key"]][column_to_count].value_counts().get("NEUTRAL", 0)
            negative_count = sentences_df[sentences_df["Key"] == row["Key"]][column_to_count].value_counts().get("NEGATIVE", 0)
            
            try:
                reviews_df.at[index, "Proportion of Sentences Positively Mentioning " + topic] = positive_count / (positive_count + neutral_count + negative_count)
            except ZeroDivisionError:
                reviews_df.at[index, "Proportion of Sentences Positively Mentioning " + topic] = 0.0
                
            try:    
                reviews_df.at[index, "Proportion of Sentences Neutrally Mentioning " + topic] = neutral_count / (positive_count + neutral_count + negative_count)
            except ZeroDivisionError:
                reviews_df.at[index, "Proportion of Sentences Neutrally Mentioning " + topic] = 0.0
                
            try:
                reviews_df.at[index, "Proportion of Sentences Negatively Mentioning " + topic] = negative_count / (positive_count + neutral_count + negative_count)
            except ZeroDivisionError:
                reviews_df.at[index, "Proportion of Sentences Negatively Mentioning " + topic] = 0.0

    
    
    
    # now we need to make one more tab where the sentiment is unpivoted
    
    
    cols_to_unpivot = []
    for topic in topic_list:
        cols_to_unpivot.append("Proportion of Sentences Positively Mentioning " + topic)
        cols_to_unpivot.append("Proportion of Sentences Neutrally Mentioning " + topic)
        cols_to_unpivot.append("Proportion of Sentences Negatively Mentioning " + topic)
    
    
    cols_to_use_as_ids = reviews_df.columns.tolist()
    for col in cols_to_unpivot:
        cols_to_use_as_ids.remove(col)

    
    
    unpivoted_df = pd.melt(reviews_df, id_vars=cols_to_use_as_ids, value_vars=cols_to_unpivot)
    
    unpivoted_df["Proportion Negative"] = 0.0
    unpivoted_df["Proportion Neutral"] = 0.0
    unpivoted_df["Proportion Positive"] = 0.0

    unpivoted_df["Topic"] = ""
    for index, row in tqdm(unpivoted_df.iterrows(), total=unpivoted_df.shape[0]):
        
        
        
        # for topic in reversed topic list
        for topic in sorted(topic_list, key=len, reverse=True):
            if row["variable"] in ["Proportion of Sentences Positively Mentioning " + topic, "Proportion of Sentences Neutrally Mentioning " + topic, "Proportion of Sentences Negatively Mentioning " + topic]:
                unpivoted_df.at[index, "Topic"] = topic
                if row["variable"] == "Proportion of Sentences Positively Mentioning " + topic:
                    unpivoted_df.at[index, "Proportion Positive"] = row["value"]
                if row["variable"] == "Proportion of Sentences Neutrally Mentioning " + topic:
                    unpivoted_df.at[index, "Proportion Neutral"] = row["value"]
                if row["variable"] == "Proportion of Sentences Negatively Mentioning " + topic:
                    unpivoted_df.at[index, "Proportion Negative"] = row["value"]                
                break
        
    
    # not remove the variable col
    unpivoted_df = unpivoted_df.drop(columns=["variable"])
    
    
    
    # now lets group together every row with same key and topic and sum the proportions
    grouped_df = unpivoted_df.groupby(["Key", "Promoted Review", "Amazon.com", "BestBuy.com", "Costco.com", "HomeDepot.com", "Lowes.com", "Walmart.com", "review_date", "star_rating", "Brand", "Model No.", "Price", "Topic"], dropna=False)[["Proportion Negative", "Proportion Neutral", "Proportion Positive"]].sum().reset_index()
    
    
    
    
    

        
        
    
    
    
    print("Exporting to:", output_file)
    #output_file = output + " Predicted Tags and Sentiments.xlsx"
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    sentences_df.to_excel(writer, sheet_name='Sentences', index=False)
    reviews_df.to_excel(writer, sheet_name='Reviews', index=False)
    #unpivoted_df.to_excel(writer, sheet_name='Unpivoted', index=False)
    grouped_df.to_excel(writer, sheet_name='Grouped By', index=False)
    writer._save()        
        
        
    

if __name__ == "__main__":
    main(reviews_df, sentences_df, output_file)    
    
    
