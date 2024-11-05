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

    # review_df, sentences_df = SentimentBreakdown.main(starting_df, "outputs/sentiment_outputs/"+ appliance_type +" Sentiment Breakdown " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    
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

    # review_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker Sentiment Breakdown 2024_2_20.xlsx", "Reviews")
    # sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker Sentiment Breakdown 2024_2_20.xlsx", "Sentences")

    ############################################################################################
    
    
    # tagged_reviews_df, tagged_sentences_df = Tagger.main(tag_file, review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " Tagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "lemma") 
    # tagged_reviews_df, tagged_sentences_df = gpt_tagger.main("inputs/tag_lists/Coffee Maker GPT Tag List.xlsx", review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " GPTagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", appliance_type)
    
    print("done 2")

    ############################################################################################
    # Crashed? Then just comment out this part.Make sure the excel files are of today's date.
    ############################################################################################

    import pandas as pd
        
    def excelSheetToDf(fileName, sheetName):
        # load the dataset
        excel_file = pd.ExcelFile(fileName)
        df = excel_file.parse(sheetName)
        return (df)

    tagged_reviews_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker GPTagged 2024_2_27 gpt-4-0125-preview.xlsx", "Reviews")
    tagged_sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker GPTagged 2024_2_27 gpt-4-0125-preview.xlsx", "Sentences")

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

    # tagged_reviews_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker Tags and Sentiment Predictions 2024_2_27.xlsx", "Reviews")
    # tagged_sentences_df = excelSheetToDf(r"C:\Users\sdacoop2\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\sentiment_outputs\Coffee Maker Tags and Sentiment Predictions 2024_2_27.xlsx", "Sentences")

    ############################################################################################
    
    
    custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df = custom_sentiment_calculation.main(tagged_and_predicted_review_df, tagged_and_predicted_sentence_df, "outputs/sentiment_outputs/" + appliance_type + " custom sentiment " +  str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    print("done 4")
    
    #return tagged_and_predicted_review_df, tagged_and_predicted_sentence_df
    return custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df

if __name__ == "__main__":
    
    starting_df = pd.read_excel("outputs/Reviews/Combined Coffee Maker Reviews 2024_2_14.xlsx")

    appliance_type = "Coffee Maker"
    tag_file = "inputs/tag_lists/Coffee Maker GPT Tag List.xlsx"
    sentiment_topics = ["Performance", "noise level", "Cleanability", "Quality", "reliability", "Water filter installation", "Cleaning cycle", "Cleaning frequency", "App experience", "Wifi and bluetooth connectivity", "Counter top space/Size", "Grind weight", "Taste", "Appearance", "Colors", "Materials", "Temperature", "Grinder static", "Smell/Aroma", "Messy grinds", "Failures", "Malfunctions", "Efficiency", "consistency", "brewing time", "grinding capability", "safety", "maintenance", "Durability", "versatility", "convenience", "compatibility", "customization", "capacity", "dispensing", "control panel", "grind settings", "brew strength", "temperature control", "grinder capacity", "drip mechanism", "brew size options", "water capacity", "energy consumption", "automatic cleaning", "brew basket", "Coffee filters", "User Manual", "Customer support", "SCA - Specialty Coffee Association", "water filter life", "brew pause function", "water level detection", "portability", "accessories", "cup size options", "easy assembly", "knob controls", "precision", "grind and brew function", "maintenance alerts"]
    main(starting_df, appliance_type, tag_file, sentiment_topics)