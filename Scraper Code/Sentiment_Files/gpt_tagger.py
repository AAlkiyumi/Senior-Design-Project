""" This program tags mentioned topics at the sentence level. It then applies the tags to the review level. 
    Josh Phillips, RAC Data Scientist, 2024 """

import pandas as pd
from tqdm import tqdm
import time
from openai import OpenAI

import api_keys
client = OpenAI(api_key=api_keys.get_open_ai_secret_key())

from queue import Queue
from threading import Thread



def promotedTagger(data_frame):
    """ special tag that gets its own function because it searches the review to see if it was part of a promotion"""

    print("\nTagging for the Promoted Review tag.")
    print("Searching for the following phrases: ")
    print("'This review was collected as part of a promotion'")  # Promoted reviews must contain this sentence
    promoted_keys = []
    result = []
    for index, row in tqdm(data_frame.iterrows(), total=data_frame.shape[0]):
        row_tag = False
        if str("review was collected as part of a promotion") in str(row['review_text']).lower():
            row_tag = True
            promoted_keys += [row['Key']]  # Stores the Key of promoted reviews
        result += [row_tag]
    return {"Promoted Review Bool List": result, "Promoted Keys": promoted_keys}

def predict_topics_with_gpt(topics, sentence, appliance_type):
    """
    Uses OpenAI service
    """
    model_name = "gpt-4o" # switching to 4o because it is the most recent model and cheaper than preview
    # model_name = "gpt-4-0125-preview"
    # model_name ="gpt-3.5-turbo"
    output = "Not Available"
    
    retries = 5
    print("-"*80)
    print(sentence)
    while retries > 0:
        try:
            response = client.chat.completions.create(model=model_name,
            messages=[
                {"role": "user",
                    "content": f"In the context of {appliance_type} online reviews, does the following sentence talk about any of the folowing topics {str(topics)}? Return only a list of the relevant topics from my list and nothing else. Sentence: {sentence}"}
            ],
            max_tokens=50,
            temperature=0,
            timeout=3)
            output = response.choices[0].message.content
            
            print("\n"+output+"\n")
            break
        except Exception as e:
            retries -= 1
            if retries > 0:
                time.sleep(3)
            else:
                print("Wasn't able to detect the relevant. Assigning Not Available\n")
                print(e)
                
    return output, model_name
    
    
def gpt_tagger_worker(n, q):
    global topics_only_list
    global sentences_df
    global appliance_type
    
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                index = data[0]
                row = data[1]
                
                
                if len(str(row["sentence"])) > 2:
                
                    if "this review was collected as part of a promotion" in str(row["sentence"]).lower():
                        gpts_response_for_topics = ""
                        try:
                            model_name = model_name
                        except Exception:
                            model_name = ""
                    else:
                        gpts_response_for_topics, model_name = predict_topics_with_gpt(topics_only_list, str(row["sentence"]), appliance_type)
                        
                else:
                    print("-"*80)
                    print(str(row["sentence"]), "not long enough to predict topics")
                    gpts_response_for_topics = ""
                
                if gpts_response_for_topics == "Not Available":
                    break
                
                # if the topic appeared in gpts response then we will tag the sentence as having that topic
                
                
                # this is to fix a bug where topics like "app" were being tagged as "app" and "appliances"
                sorted_topics_only_list = sorted(topics_only_list, key=len, reverse=True)
                
                topics_gpt_found = []
                for topic in sorted_topics_only_list:
                    if topic in gpts_response_for_topics:
                        sentences_df.at[index, topic] = True
                        topics_gpt_found += [topic]
                        
                        gpts_response_for_topics = gpts_response_for_topics.replace(topic, "")
            
                if  topics_gpt_found == []:
                    sentences_df.at[index, "Untagged"] = True

                
                print("Great Success")
                q.task_done()
            except Exception as e:
                print(e)
                print("Couldn't get data from", data)
                q.task_done()
                
        except Exception as e:
            print("Thread", n, "has joined")
            break

things_to_tag_q = Queue(maxsize=0)
topics_only_list = []
sentences_df = pd.DataFrame()
appliance_type = ""
CONCURRENCY = 50

def main(new_version_of_tag_file, reviews_df, sentences_df_original, output_file, appliance_type_original):
    
    global things_to_tag_q
    things_to_tag_q = Queue(maxsize=0)
    
    global topics_only_list
    topics_only_list = []
    
    global sentences_df
    sentences_df = sentences_df_original
    
    global appliance_type
    appliance_type = appliance_type_original
    
    
    
    try:
        # the first thing we are going to do is read in the new_version_of_tag_file
        # the headers are going to be the topics
        # the first row will be the context we are looking for of the topic
        
        tag_topic_and_context_df = pd.read_excel(new_version_of_tag_file)
        topics_only_list = tag_topic_and_context_df.columns.tolist()
        
        
        
            
        # now we are going to see if the reviews are part of a promotion
        promoted_tagger_dict = promotedTagger(reviews_df)
        reviews_df["Promoted Review"] = promoted_tagger_dict["Promoted Review Bool List"]
        
        sentences_df["Promoted Review"] = False
        
        # now lets tag all the sentences that originated from a promoted review
        for index, row in sentences_df.iterrows():
            if row["Key"] in promoted_tagger_dict["Promoted Keys"]:
                sentences_df.at[index, "Promoted Review"] = True
                
        # now lets create a new column for each topic in the sentences_df
        for topic in topics_only_list + ["Untagged"]:
            sentences_df[topic] = False
            reviews_df[topic] = False
            
        
        # now we are going to use gpt to predict the topics for each sentence
        for index, row in tqdm(sentences_df.iterrows(), total=sentences_df.shape[0]):
            
            things_to_tag_q.put([index, row])
            
        threads = []
        for i in range(CONCURRENCY):
            threads += [Thread(target=gpt_tagger_worker, args=(i, things_to_tag_q))]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
            
            
                
        # now we need to match any tagged sentences to the review with the matching key
        for index, row in reviews_df.iterrows():
            matching_sentences = sentences_df[sentences_df["Key"] == row["Key"]]
            for topic in topics_only_list + ["Untagged"]:
                if True in matching_sentences[topic].tolist():
                    reviews_df.at[index, topic] = True
                    
        # output to excel file specified above
        output_file = output_file.split(".xlsx")[0] + ".xlsx"
        print("Exporting to:", output_file)
        
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        # Don't convert url-like strings to urls.
        writer.book.strings_to_urls = False
        
        sentences_df.to_excel(writer, sheet_name='Sentences', index=False)
        reviews_df.to_excel(writer, sheet_name='Reviews', index=False)
        writer._save()
    
    except KeyboardInterrupt:
        output_file = output_file.split(".xlsx")[0] + " Backup.xlsx"
        print("Exporting to:", output_file)
        
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        # Don't convert url-like strings to urls.
        writer.book.strings_to_urls = False
        
        sentences_df.to_excel(writer, sheet_name='Sentences', index=False)
        reviews_df.to_excel(writer, sheet_name='Reviews', index=False)
        writer._save()
        
    return reviews_df, sentences_df
    
if __name__ == '__main__':
    tag_file = input("Enter name of tag file")
    reviews_file_name = input("Enter name of reviews df file")
    reviews_sheet_name = input("Enter name of reviews sheet")
    sentences_file_name = input("Enter name of sentences df file")
    sentences_sheet_name = input("Enter name of sentences sheet")
    
    output_file = input("Enter name of output file")
    
    main(tag_file, pd.read_excel(reviews_file_name, sheet_name=reviews_sheet_name), pd.read_excel(sentences_file_name, sheet_name=sentences_sheet_name), output_file)