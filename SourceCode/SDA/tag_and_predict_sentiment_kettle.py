import sys
import pandas as pd
from datetime import datetime

# Add the Sentiment_Files folder to the path
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Sentiment_Files"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["secret_api_keys"]))

# import the sentiment files
import SentimentBreakdown
import Tagger
import predicting_sentiment
import gpt_tagger
import custom_sentiment_calculation


def main(starting_df, appliance_type, tag_file, sentiment_topics):

    review_df, sentences_df = SentimentBreakdown.main(starting_df, "outputs/sentiment_outputs/"+ appliance_type +" Sentiment Breakdown " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    
    print("done")
    ############################################################################################
    # Crashed? Then just comment out this part.Make sure the excel files are of today's date.
    ############################################################################################

    # import pandas as pd
        
    # def excelSheetToDf(fileName, sheetName):
    #     # load the dataset
    #     excel_file = pd.ExcelFile(fileName)
    #     df = excel_file.parse(sheetName)
    #     return (df)

    # review_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle Sentiment Breakdown 2024_2_20.xlsx", "Reviews")
    # sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle Sentiment Breakdown 2024_2_20.xlsx", "Sentences")

    ############################################################################################
    
    
    # tagged_reviews_df, tagged_sentences_df = Tagger.main(tag_file, review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " Tagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "lemma") 
    tagged_reviews_df, tagged_sentences_df = gpt_tagger.main("inputs/tag_lists/Electric Kettle GPT Tag List.xlsx", review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " GPTagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", appliance_type)
    
    print("done 2")

    ############################################################################################
    # Crashed? Then just comment out this part.Make sure the excel files are of today's date.
    ############################################################################################

    # import pandas as pd
        
    # def excelSheetToDf(fileName, sheetName):
    #     # load the dataset
    #     excel_file = pd.ExcelFile(fileName)
    #     df = excel_file.parse(sheetName)
    #     return (df)

    # tagged_reviews_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle GPTagged 2024_2_27 gpt-4-0125-preview.xlsx", "Reviews")
    # tagged_sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle GPTagged 2024_2_27 gpt-4-0125-preview.xlsx", "Sentences")

    ############################################################################################
    
    
    tagged_and_predicted_review_df, tagged_and_predicted_sentence_df = predicting_sentiment.main(tagged_reviews_df, tagged_sentences_df, "outputs/sentiment_outputs/" + appliance_type + " Tags and Sentiment Predictions " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", sentiment_topics)
    print("done 3")

    ############################################################################################
    # Crashed? Then just comment out this part.Make sure the excel files are of today's date.
    ############################################################################################

    # import pandas as pd
        
    # def excelSheetToDf(fileName, sheetName):
    #     # load the dataset
    #     excel_file = pd.ExcelFile(fileName)
    #     df = excel_file.parse(sheetName)
    #     return (df)

    # tagged_reviews_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle Tags and Sentiment Predictions 2024_2_27.xlsx", "Reviews")
    # tagged_sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Electric Kettle Tags and Sentiment Predictions 2024_2_27.xlsx", "Sentences")

    ############################################################################################
    
    
    custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df = custom_sentiment_calculation.main(tagged_and_predicted_review_df, tagged_and_predicted_sentence_df, "outputs/sentiment_outputs/" + appliance_type + " custom sentiment " +  str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    print("done 4")
    
    #return tagged_and_predicted_review_df, tagged_and_predicted_sentence_df
    return custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df

if __name__ == "__main__":
    
    starting_df = pd.read_excel("outputs/Reviews/Combined Electric Kettle Reviews 2024_3_25.xlsx")

    appliance_type = "Electric Kettle"
    tag_file = "inputs/tag_lists/Electric Kettle GPT Tag List.xlsx"
    sentiment_topics = ["Appearance", "Performance", "Noise", "Speed", "Quality", "Durability", "Reliability", "Efficiency", "Design", "Size", "Ease of Use", "Safety", "Temperature Control", "Power Consumption", "Versatility", "Brand", "Price", "Cleaning", "Capacity", "Portability", "Customer Service", "Accessories", "Flavor", "Weight", "Application", "Energy Efficiency", "Residue"]
    main(starting_df, appliance_type, tag_file, sentiment_topics)