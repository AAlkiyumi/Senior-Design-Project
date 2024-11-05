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

    # review_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder Sentiment Breakdown 2024_4_25.xlsx", "Reviews")
    # sentences_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder Sentiment Breakdown 2024_4_25.xlsx", "Sentences")

    ############################################################################################
    
    
    # tagged_reviews_df, tagged_sentences_df = Tagger.main(tag_file, review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " Tagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "lemma") 
    # tagged_reviews_df, tagged_sentences_df = gpt_tagger.main("inputs/tag_lists/Electric Coffee Grinder GPT Tag List.xlsx", review_df, sentences_df, "outputs/sentiment_outputs/" + appliance_type + " GPTagged " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", appliance_type)
    
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

    # tagged_reviews_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder GPTagged 2024_4_26 gpt-3.5-turbo.xlsx", "Reviews")
    # tagged_sentences_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder GPTagged 2024_4_26 gpt-3.5-turbo.xlsx", "Sentences")

    ############################################################################################
    
    
    # tagged_and_predicted_review_df, tagged_and_predicted_sentence_df = predicting_sentiment.main(tagged_reviews_df, tagged_sentences_df, "outputs/sentiment_outputs/" + appliance_type + " Tags and Sentiment Predictions " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", sentiment_topics)
    print("done 3")

    ############################################################################################
    # Crashed? Then just comment out this part.Make sure the excel files are of today's date.
    ############################################################################################

    import pandas as pd
        
    def excelSheetToDf(fileName, sheetName):
        # load the dataset
        excel_file = pd.ExcelFile(fileName)
        df = excel_file.parse(sheetName)
        return (df)

    tagged_and_predicted_review_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder Tags and Sentiment Predictions 2024_4_26.xlsx", "Reviews")
    tagged_and_predicted_sentence_df = excelSheetToDf(r"outputs\sentiment_outputs\Electric Coffee Grinder Tags and Sentiment Predictions 2024_4_26.xlsx", "Sentences")

    ############################################################################################
    
    
    custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df = custom_sentiment_calculation.main(tagged_and_predicted_review_df, tagged_and_predicted_sentence_df, "outputs/sentiment_outputs/" + appliance_type + " custom sentiment " +  str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    print("done 4")
    
    #return tagged_and_predicted_review_df, tagged_and_predicted_sentence_df
    return custom_sentiment_calculation__review_df, custom_sentiment_calculation__sentence_df

if __name__ == "__main__":
    
    starting_df = pd.read_excel("outputs/Reviews/Combined Electric Coffee Grinder Reviews 2024_4_25.xlsx")

    appliance_type = "Electric Coffee Grinder"
    tag_file = "inputs/tag_lists/Electric Coffee Grinder GPT Tag List.xlsx"
    sentiment_topics = [
    "Performance", "Speed", "Noise Level", "Cleanability", "Quality", "Setup",
    "Reliability", "Cleaning Frequency", "App Experience", "Wifi And Bluetooth Connectivity",
    "Countertop Space", "Grind Weight", "Appearance", "Colors", "Materials",
    "Temperature", "Messiness", "Grinder Static", "Smell", "Messy Grinds",
    "Failures", "Malfunctions", "Efficiency", "Consistency", "Grinding Capability",
    "Safety", "Maintenance", "Durability", "Versatility", "Convenience",
    "Compatibility", "Customization", "Capacity", "Dispensing", "Control Panel",
    "Settings", "User Interface", "Grind Settings", "Automatic Cleaning", "Portability",
    "Accessories", "Cup Size Options", "Easy Assembly", "Bean Hopper Capacity",
    "Knob Controls", "Precision", "Maintenance Alerts", "Weighing", "Grind Size Adjustment"
    ]

    main(starting_df, appliance_type, tag_file, sentiment_topics)