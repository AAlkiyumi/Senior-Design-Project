import sys
from datetime import datetime, timedelta
\

# Add the Scraped_Output_Formatters folder to the path
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraped_Output_Formatters"]))

# import the post_processing file from the Scraped_Output_Formatters folder
import post_processing_formatter
import mapped_to_correct_stores
import pandas as pd

global n_days_ago

def days_back(n_days):
    # input: integer n_days (number of days to go back)
    # output: datetime n_days_ago (round to the start of the day)
    todays_date = datetime.now()
    n_days_ago = (todays_date - timedelta(days=n_days)).replace(hour=0, minute=0, second=0, microsecond=0)
    return n_days_ago


def excelSheetToDf(fileName, sheetName):
    # load the dataset
    excel_file = pd.ExcelFile(fileName) 
    df = excel_file.parse(sheetName)
    return (df)  


def main():
    
    # See how far back to scrape
    # number_of_days_back_to_scrape = int(input("Enter how many days back to scrape? "))
    number_of_days_back_to_scrape = 10000
    n_days_ago = days_back(number_of_days_back_to_scrape)


    slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Combined Slow Cooker Reviews 2024_4_15" + ".xlsx", "Sheet1")
    multi_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Combined Multi Cooker Reviews 2024_4_15" + ".xlsx", "Sheet1")
    pressure_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Combined Pressure Cooker Reviews 2024_4_16" + ".xlsx", "Sheet1")


    ##############################################
    #                                            #
    #             COMBINE AND EXPORT             #
    #                                            #
    ##############################################

    list_of_stores = ["Amazon.com", "BestBuy.com", "Costco.com", "Walmart.com", "Homedepot.com", "Lowes.com"]

    # combine all the df with the same appliance type
    combined_wet_cooker_df = pd.concat([slow_cooker_df, multi_cooker_df, pressure_cooker_df], ignore_index=True)
    print(combined_wet_cooker_df)
    # drop the duplicate rows
    combined_wet_cooker_df.drop_duplicates()

    # filter out the reviews that are too old
    combined_wet_cooker_df = combined_wet_cooker_df[combined_wet_cooker_df["review_date"] > n_days_ago]

    # map the reviews that appear on multiple sites to a single row in the dataframe
    combined_wet_cooker_df = mapped_to_correct_stores.map_duped_reviews_to_shared_stores(combined_wet_cooker_df, list_of_stores)

    # get rid of any cols starting with "Unnamed"
    combined_wet_cooker_df = combined_wet_cooker_df.loc[:, ~combined_wet_cooker_df.columns.str.contains('^Unnamed')]
    print(combined_wet_cooker_df)
    #export the df to excel
    combined_wet_cooker_df.to_excel("outputs/Reviews/" + "Combined Wet Cooking Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)


if __name__ == "__main__":
    main()