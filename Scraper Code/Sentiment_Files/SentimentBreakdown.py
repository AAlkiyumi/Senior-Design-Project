"""" This will break down reviews into sentences, assign everything with a unique key,
     and give initial sentiment scores from -1 to 1 using the natural language toolkit
     Josh Phillips, RAC co-op, Spring 2021 """

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm

nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('wordnet')
import re

sid = SentimentIntensityAnalyzer()


def excelSheetToDf(file_name, sheet_name):
    """
    input: string fileName: name of excel file ending in .xlsx
           string sheetName: name of the sheet you want to pull from fileName
    output: pandas dataframe df: uses the first row in the excel file as headers
    """
    # load the dataset
    excel_file = pd.ExcelFile(file_name)
    df = excel_file.parse(sheet_name)
    return df


def filterDataFrame(df, column_name):
    """
    input: dataFrame, ColumnName
    output: dataFrame that has removed rows with null entries in ColumnName
    """
    #bool_series = pd.notnull(data_frame[column_name])
    #df = data_frame[bool_series]
    df.fillna("", inplace=True)
    return df


def lemmatise(sentence, stop_words):
    """
    input: sentence, any stop words to remove from the sentence
    output: lemmatised version of the sentence
    """
    words = nltk.word_tokenize(sentence)
    # Remove punctuations and make lowercase
    words = [word.replace("'", "") for word in words]
    words = [word.lower() for word in words if word.isalpha()]
    # Lemmatisation
    lem = WordNetLemmatizer()
    words = [lem.lemmatize(word) for word in words if not (word in stop_words)]  # lem word if word not in stop_words
    lemma = " ".join(words)
    return lemma


def main(starting_df, output_file):
    # Put into a data frame and fill the nan values with empty strings
    starting_df = filterDataFrame(starting_df, "review_text")

    # get the sentiment scores using Sentiment Intensity Analyzer
    sentiment_scores = []
    for index, review in tqdm(enumerate(starting_df['review_text']), total=starting_df.shape[0]):
        sentiment_scores += [sid.polarity_scores(str(review))['compound']]

    
    starting_df["review_sentiment_score"] = sentiment_scores

    # importing stop words for lemma function
    stop_words = set(stopwords.words("english"))

    # remove these words from the default stopwords list because they are important to the meaning of a review
    negation = ["mustn't", "aren't", 'ain', 'mightn', 'needn', 'wasn', "shan't",
                'hadn', "mightn't", "isn't", 'hasn', 'shan', "hadn't", 'shouldn', "needn't",
                'doesn', 'haven', 'no', "wasn't", 'mustn', "haven't", 'didn', "weren't",
                "wouldn't", "don't", "couldn't", 'weren', 'nor', 'aren', "didn't", 'wouldn',
                'isn', "hasn't", 'couldn', 'don', "doesn't", "won't", 'off', 'on', "shouldn't", 'not',
                'does', 'did']
    for word in negation:
        stop_words.remove(word)

    # add these words into our stop word list because there are so many promoted reviews and we'll
    # search fot those separately
    promoted = ['review', 'collected', 'part', 'promotion', 'rating', 'provided', 'verified',
                'purchaser']
    for word in promoted:
        stop_words.add(word)



    keys = []
    sentences_only = []
    lemmas = []
    sentiment_scores = []
    
    
    
    row_list = []
    
    # begin going through the review data frame and getting the info for the sentence data frame
    print("Performing Sentiment Analysis")
    for index, row in tqdm(starting_df.iterrows(), total=starting_df.shape[0]):
        
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
            lemmas += [lemmatise(sentence, stop_words)]
            sentiment_scores += [sid.polarity_scores(sentence)['compound']]
            row_list.append(row.to_dict())
            
    # Pack the values into the sentence data frame
    sentences_and_sentiment_scores_df = pd.DataFrame(row_list)
    
    print(sentences_and_sentiment_scores_df.shape[0])
    # find the location of the review_text col in the starting_df
    review_text_col_index = starting_df.columns.get_loc("review_text")
    
    # add the sentences_only and lemmas to the starting_df at the location of the review_text col
    sentences_and_sentiment_scores_df.insert(loc=review_text_col_index+1, column="sentence", value=sentences_only)
    sentences_and_sentiment_scores_df.insert(loc=review_text_col_index+2, column="lemma", value=lemmas)
    sentences_and_sentiment_scores_df.insert(loc=review_text_col_index+3, column="sentence_sentiment_score", value=sentiment_scores)
    
        
            
        

    # output to the excel file specified above
    print("Exporting to:", output_file)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    # Don't convert url-like strings to urls.
    writer.book.strings_to_urls = False
    
    starting_df.to_excel(writer, sheet_name='Reviews', index=False)
    sentences_and_sentiment_scores_df.to_excel(writer, sheet_name='Sentences',index=False)
    writer._save()

    return starting_df, sentences_and_sentiment_scores_df

if __name__ == '__main__':
    # When run as a standalone program, the user needs to specify:
    # Starting DataFrame excel file & sheet name
    # Output File Name (Will overwrite if it already exists
    # Value to increment all keys by
    custom_file_name = input("Enter the name of the xlsx file containing the starting data frame: ")
    custom_sheet_name = input("Enter the sheet name: ")
    custom_output_file = input("Enter the name of the output file to create: ")
    custom_start_df = excelSheetToDf(custom_file_name, custom_sheet_name)
    main(custom_start_df, custom_output_file)
