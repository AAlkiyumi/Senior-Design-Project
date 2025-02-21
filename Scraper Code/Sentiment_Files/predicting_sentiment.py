""" For every tagged sentence, this program makes a prediction whether
    or not the sentence is positive, neutral or negative sentiment. It
    then matches sentences to reviews with the same key (Unique Identifier)
    Josh Phillips, RAC co-op, Spring 2021 """


import pandas as pd
from tqdm import tqdm
import time

import boto3
import api_keys


from queue import Queue
from threading import Thread

from openai import OpenAI

client = OpenAI(api_key=api_keys.get_open_ai_secret_key())

class PredictSentiment:
    def __init__(self):
        self.comprehend = boto3.client("comprehend",
                                  region_name="us-east-1",
                                  aws_access_key_id=api_keys.get_aws_access_key_id(),
                                  aws_secret_access_key=api_keys.get_aws_secret_access_key())

    def predict_with_comprehend(self, row, topic):
        """
        Uses AWS Comprehend service
        """
        
        if len(str(row['sentence'])) <= 1:
            return "NEUTRAL"
        
        # response = self.comprehend.detect_sentiment(Text=row['sentence'], LanguageCode='en')
        response = self.comprehend.detect_sentiment(Text=str(row['sentence']), LanguageCode='en')
        output = response["Sentiment"].upper()
        
        return output

    def predict_with_gpt(self, sentence, topic):
        """
        Uses OpenAI service
        """
        
        retries = 5
        output = "NOT AVAILABLE"
        while retries > 0:
            try:
                
                if topic != "Noise":
                    response = client.chat.completions.create(model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user",
                            "content": f"Analyze the following product review for topic: {topic} and determine if the sentiment reguarding the topic is: POSITIVE, NEGATIVE or NEUTRAL. Return only a single word, either POSITIVE, NEGATIVE or NEUTRAL: {sentence}"}
                    ],
                    max_tokens=10,
                    temperature=0,
                    timeout=3)
                if topic == "Noise":
                    print(str(sentence))
                    response = client.chat.completions.create(model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user",
                            "content": f"Analyze the following product review for topic: {topic} and determine if the sentiment reguarding the topic is: POSITIVE, NEGATIVE or NEUTRAL. Quiet is POSITIVE and Loud or unsual noises is NEGATIVE. Return only a single word, either POSITIVE, NEGATIVE or NEUTRAL: {sentence}"}
                    ],
                    max_tokens=10,
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
                    print("Wasn't able to detect sentiment. Assigning Not Available\n")
                    print(e)

        return output.upper()


def excelSheetToDf(fileName, sheetName):
    """
    input: string fileName: name of excel file ending in .xlsx
           string sheetName: name of the sheet you want to pull from fileName
    output: pandas dataframe df: uses the first row in the excel file as headers
    """
    excel_file = pd.ExcelFile(fileName)
    df = excel_file.parse(sheetName)
    return df
    
    
def predict_sentiment_worker(n, q):
    global topics
    global sentiment_predictor
    global data_frame
    
    while True:
        try:
            data = q.get(block=False, timeout=1)
            index = data[0]
            row = data[1]
            
            try:
                # get the topics that are mentioned in the sentence
                topics_mentioned_in_sentence = []
                for topic in topics:
                    if row[topic]:
                        topics_mentioned_in_sentence.append(topic)
                

                # Use AWS comprehend to make a sentiment prediction on the sentence
                if topics_mentioned_in_sentence != []:
                    
                    if "this review was collected as part of a promotion" in str(row['sentence']).lower():
                        sentence_sentiment = "NEUTRAL"
                    
                    elif "Noise" in topics_mentioned_in_sentence:
                        # all sentences with noise get sent to ChatGPT
                        sentence_sentiment = "MIXED"
                    else:
                        sentence_sentiment = sentiment_predictor.predict_with_comprehend(row, topics)
                else:
                    sentence_sentiment = "Not Mentioned"
                    
                
                for topic in topics:
                    if topic in topics_mentioned_in_sentence:
                        if sentence_sentiment != "MIXED":
                            data_frame.loc[index, 'Predicted ' + topic + ' Sentiment'] = sentence_sentiment
                        else:
                            target_sentiment = sentiment_predictor.predict_with_gpt(row['sentence'], topic)
                            data_frame.loc[index, 'Predicted ' + topic + ' Sentiment'] = target_sentiment
                            
                print("Great Success")
                q.task_done()
                
            except Exception as e:
                print(e)
                print("Couldn't get data from", data)
                q.task_done()
        
        except Exception as e:
            print("Thread", n, "has joined")
            break
    
things_to_predict_q = Queue(maxsize=0)
CONCURRENCY = 50
topics = None
sentiment_predictor = None
data_frame = None

def main(reviews_df, sentences_df, output_file, topics_original):
    
    global things_to_predict_q
    things_to_predict_q = Queue(maxsize=0)
    
    global topics
    topics = topics_original
    
    # making a predictor using our Class
    global sentiment_predictor
    sentiment_predictor = PredictSentiment()
    
    global data_frame
    data_frame = sentences_df
    
    
    #TODO need to work on this file. Will need to pass in our unique comprehend and openai keys so we dont use eachothers credits
    
    print("Loading the dataframe")
    #data_frame = excelSheetToDf(previous_output, "Sentences")
    
    
    
    
    # make the prediction columns for each topic
    for topic in topics:
        data_frame['Predicted ' + topic + ' Sentiment'] = 'Not Mentioned'
    
    
    
    
    
    print("Loading up the queue of the reviews at the sentence level")
    for index, row in tqdm(data_frame.iterrows(), total=data_frame.shape[0]):
        things_to_predict_q.put([index, row])

    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=predict_sentiment_worker, args=(i, things_to_predict_q))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
        
        
    
        
        
        
                
                
        

    # Matching the Sentences to the reviews
    print("Loading the entire reviews as a whole into a data frame")
    #review_data_frame = excelSheetToDf(previous_output, "Reviews")
    review_data_frame = reviews_df

    # specific to window air conditioners, consider loading this from a file
    a_list_of_cols_to_be_int = []
    # if the column is True False, we want to convert it to 1 0
    for col in review_data_frame.columns:
        # if all values in col are True or False, add it
        if review_data_frame[col].dtype == bool:
            a_list_of_cols_to_be_int.append(col)
            
        print(a_list_of_cols_to_be_int)

    for col in a_list_of_cols_to_be_int:
        review_data_frame[col] = review_data_frame[col].astype(int)
        
        
    print("Matching Sentences with Reviews")
    
    for index, topic in tqdm(enumerate(topics), total=len(topics)):
        
        print("-"*100)

        # add new columns: neg neu pos, if there is at least one training example with that sentiment. Initialize
        # everything in the column to 0 (some topics like stopped working has no positive sentiment)
    
        print(topic)
        review_data_frame['Negatively Mentions ' + topic] = 0
        review_data_frame['Neutrally Mentions ' + topic] = 0
        review_data_frame['Positively Mentions ' + topic] = 0
        

        # change the rows to reflect the predicted sentiments
        print(data_frame[data_frame[topic] == 1])
        
        
        for idx, row in data_frame[data_frame[topic] == 1].iterrows():
            if row['Predicted ' + topic + ' Sentiment'] == "NEGATIVE":
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Negatively Mentions ' + topic])
                review_data_frame.loc[review_data_frame.Key == row['Key'], 'Negatively Mentions ' + topic] = 1
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Negatively Mentions ' + topic])
            elif row['Predicted ' + topic + ' Sentiment'] == "NEUTRAL":
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Neutrally Mentions ' + topic])
                review_data_frame.loc[review_data_frame.Key == row['Key'], 'Neutrally Mentions ' + topic] = 1
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Negatively Mentions ' + topic])
            elif row['Predicted ' + topic + ' Sentiment'] == "POSITIVE":
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Positively Mentions ' + topic])
                review_data_frame.loc[review_data_frame.Key == row['Key'], 'Positively Mentions ' + topic] = 1
                print(review_data_frame.loc[review_data_frame.Key == row['Key'], 'Positively Mentions ' + topic])
            else:
                print("*" * 100)
                print(row['Predicted ' + topic + ' Sentiment'])
                

    

    # add in a month column
    #review_data_frame.insert(loc=5, column='Month', value=review_data_frame['Date'].dt.month)
    #data_frame.insert(loc=5,column='Month', value=data_frame['Date'].dt.month)
    
    # add in a year column
    #review_data_frame.insert(loc=5, column="Month", value=review_data_frame['Date'].dt.month)
    #review_data_frame.insert(loc=5, column='Year', value=review_data_frame['Date'].dt.year)

    #data_frame.insert(loc=5, column='Month', value=data_frame['Date'].dt.month)
    #data_frame.insert(loc=5, column='Year', value=data_frame['Date'].dt.year)

    print("Exporting to:", output_file)
    #output_file = output + " Predicted Tags and Sentiments.xlsx"
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    # Don't convert url-like strings to urls.
    writer.book.strings_to_urls = False
    
    data_frame.to_excel(writer, sheet_name='Sentences', index=False)
    review_data_frame.to_excel(writer, sheet_name='Reviews', index=False)
    writer._save()

    return review_data_frame, data_frame

if __name__ == '__main__':
    # These are the inputs the user must provide if they want to use this as a stand-alone program
    previous_file_name = input("Enter the name of the previous file")
    output = input("Enter base name of output file")
    reviews_df = pd.read_excel(previous_file_name, sheet_name="Reviews")
    sentences_df = pd.read_excel(previous_file_name, sheet_name="Sentences")
    main(reviews_df, sentences_df, output)