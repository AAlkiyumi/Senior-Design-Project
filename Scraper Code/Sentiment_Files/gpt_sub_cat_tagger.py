import pandas as pd
from tqdm import tqdm
import time

import openai
import api_keys
openai.api_key = api_keys.get_open_ai_secret_key()

from queue import Queue
from threading import Thread



def predict_sub_cat_with_gpt(topic, sentence, appliance_type, sentiment):
    """
    Uses OpenAI service
    """
    
    model_name = "gpt-4o"
    # model_name ="gpt-3.5-turbo"
    output = "Not Available"
    
    retries = 5
    print("-"*80)
    print(sentence)
    while retries > 0:
        try:
            
            if sentiment.upper() == "POSITIVE":
                sentiment_specifier = "liked"
            if sentiment.upper() == "NEGATIVE":
                sentiment_specifier = "disliked"
            
            if sentiment.upper() == "NEUTRAL":
                return "NEUTRAL", model_name
            
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "user",
                        "content": f"In the context of {appliance_type} online reviews, the following sentence talks about the topic/theme of {str(topic)} with {str(sentiment)} sentiment. Explain what the reviewer {str(sentiment_specifier)} about the {str(appliance_type)} specifically in regards to {str(topic)} in 5 words or less."}
                ],
                max_tokens=50,
                temperature=0,
                request_timeout=3
            )
            output = response['choices'][0]['message']['content']
        
            
            
            print("\n"+output+"\n")
            break
        except Exception as e:
            retries -= 1
            if retries > 0:
                time.sleep(3)
            else:
                #print("Wasn't able to detect the relevant. Assigning Not Available\n")
                print(e)
                print()
                
    return output, model_name
    
    
def gpt_sub_cat_worker(n, q):
    #global topics_only_list
    global sentences_df
    global appliance_type
    
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                index = data[0]
                row = data[1]
                print(row)
                gpts_response_for_sub_cat, model_name = predict_sub_cat_with_gpt(str(row["Topic"]), str(row["sentence"]), appliance_type, row["Sentiment"])
                # now we will place the response in the sentences_df
                sentences_df.at[index, "Sub-Category"] = gpts_response_for_sub_cat
                
                
                # if it was not available then we will break the loop
                if gpts_response_for_sub_cat == "Not Available":
                    break
                
                #print("Great Success")
                q.task_done()
            except Exception as e:
                print("-"*80)
                print(e)
                print("*"*80)
                #print("Couldn't get data from", data)
                q.task_done()
                
        except Exception as e:
            #print("Thread", n, "has joined")
            break

things_to_tag_q = Queue(maxsize=0)
topics_only_list = []
sentences_df = pd.DataFrame()
appliance_type = ""
CONCURRENCY = 50

def main(sentences_df_original, output_file, appliance_type_original):
    
    global things_to_tag_q
    things_to_tag_q = Queue(maxsize=0)
    
    global topics_only_list
    topics_only_list = []
    
    global sentences_df
    sentences_df = sentences_df_original
    
    global appliance_type
    appliance_type = appliance_type_original
    
    
    
    try:
  
        # the first thing we are going to do is create a column for the sub-category classification
        sentences_df["Sub-Category"] = ""
        
        # now we are going to use gpt to predict the sub-cat for each sentence-topic pair
        for index, row in tqdm(sentences_df.iterrows(), total=sentences_df.shape[0]):
            things_to_tag_q.put([index, row])
            
            
        threads = []
        for i in range(CONCURRENCY):
            threads += [Thread(target=gpt_sub_cat_worker, args=(i, things_to_tag_q))]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
            
            
                    
        # output to excel file specified above
        output_file = output_file.split(".xlsx")[0] + " Sub-Cat 3" + ".xlsx"
        #print("Exporting to:", output_file)
        
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        # Don't convert url-like strings to urls.
        writer.book.strings_to_urls = False
        
        sentences_df.to_excel(writer, sheet_name='Verbatims', index=False)
        writer._save()
    
    except KeyboardInterrupt:
        output_file = output_file.split(".xlsx")[0] + " Backup.xlsx"
        #print("Exporting to:", output_file)
        
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        # Don't convert url-like strings to urls.
        writer.book.strings_to_urls = False
        
        sentences_df.to_excel(writer, sheet_name='Verbatims', index=False)
        writer._save()
        
    return sentences_df
    
if __name__ == '__main__':
    
    
    sentences_df_original = pd.read_excel("Midea Duo Verbatims.xlsx", sheet_name="Verbatims").head
    output_file = "Midea Duo Verbatims.xlsx"
    appliance_type_original = "Midea Duo"
    
    main(sentences_df_original, output_file, appliance_type_original)