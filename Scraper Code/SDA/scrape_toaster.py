import sys
from datetime import datetime, timedelta
#import pandas as pd

# Add the Scraper_Files folders to the path
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\Amazon"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\BestBuy"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\Costco"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\HomeDepot"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\Lowes"]))
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraper_Files\\Walmart"]))

# import the web scrapers from the Scraper_Files folder
import amazon2
import bestbuy2
import costco_selenium
import homedepot_selenium
import lowes_selenium
import walmart2

# Add the Scraped_Output_Formatters folder to the path
sys.path.append("\\".join(sys.path[0].split("\\")[:-1] + ["Scraped_Output_Formatters"]))

# import the post_processing file from the Scraped_Output_Formatters folder
import post_processing_formatter
import mapped_to_correct_stores


def days_back(n_days):
    # input: integer n_days (number of days to go back)
    # output: datetime n_days_ago (round to the start of the day)
    todays_date = datetime.now()
    n_days_ago = (todays_date - timedelta(days=n_days)).replace(hour=0, minute=0, second=0, microsecond=0)
    print("Scraping reviews going back until", n_days_ago)
    return n_days_ago



def main():
    
    # See how far back to scrape
    number_of_days_back_to_scrape = int(input("Enter how many days back to scrape? "))
    n_days_ago = days_back(number_of_days_back_to_scrape)
    
    
    
    ##############################################
    #                                            #
    #          PART ONE: SCRAPE REVIEWS          #
    #                                            #
    ##############################################
   
    ### Scrape Amazon.com Reviews ### Perfect
    
    # Mandatory Amazon Hrefs
    mandatory_toaster_href_list = [
        ]
           
    # """
    print("Scraping Amazon.com Reviews...")
    # amazon_toaster_df = amazon2.main(["https://www.amazon.com/s?k=slice+toaster&page=", "&crid=3AX8G3INPPPNN&qid=1713372533&sprefix=%2Caps%2C53&ref=sr_pg_"], "Slice Toaster", 20, mandatory_toaster_href_list, n_days_ago)
      
    ### Scrape BestBuy.com Reviews ### Perfect
    print("Scraping BestBuy.com Reviews...")
    # bestbuy_toaster_df = bestbuy2.main(["https://www.bestbuy.com/site/searchpage.jsp?cp=", "&id=pcat17071&st=slice+toaster"], "Slice Toaster", 3, n_days_ago)

    
    ### Scrape Walmart.com Reviews ### Perfect
    print("Scraping Walmart.com Reviews...")
    # walmart_toaster_df = walmart2.main("https://www.walmart.com/search?q=slice+toaster&affinityOverride=default&facet=retailer_type%3AWalmart&page=", "Slice Toaster", 6, n_days_ago)


    #The following use selenium, ensure vpn is turned on
    #input("Ensure you are connected to VPN to avoid getting blocked. Press Enter to continue...")

    # """
    ### Scrape Costco.com Reviews ### Perfect
    print("Scraping Costco.com Reviews...")
    # costco_toaster_df = costco_selenium.main("https://www.costco.com/CatalogSearch?dept=All&keyword=slice+toaster", 1, "Slice Toaster", 0)
   
    # """
    ### Scrape HomeDepot.com Reviews ### Perfect
    print("Scraping HomeDepot.com Reviews...")
    # homedepot_toaster_df = homedepot_selenium.main("Slice Toaster", n_days_ago, 5, "https://www.homedepot.com/s/slice%20toaster?NCNI-5&Nao=")
    
    
    ### Scrape Lowes.com Reviews ### Perfect
    print("Scraping Lowes.com Reviews...")
    # lowes_toaster_df = lowes_selenium.main("https://www.lowes.com/search?searchTerm=slice+toaster&offset=24&catalog=4294753808", 4, "Slice Toaster", n_days_ago)
    # """

    ##############################################
    #                                            #
    #          PART TWO: FORMAT REVIEWS          #
    #                                            #
    ##############################################

    ############################################################################################
    # Part 2 crashed after part 1 is done? Then just comment out part 1 and uncomment this 
    # part. Make sure the excel files are of today's date.
    ############################################################################################
    
    import pandas as pd
    
    def excelSheetToDf(fileName, sheetName):
        # load the dataset
        excel_file = pd.ExcelFile(fileName)
        df = excel_file.parse(sheetName)
        return (df)
    
    amazon_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Amazon.com Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    bestbuy_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\BestBuy.com Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    walmart_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Walmart.com Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    costco_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Costco.com Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    homedepot_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Homedepot Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    lowes_toaster_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Lowes.com Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    
    ############################################################################################


    ### Now that we've scraped all the reviews, format the dataframes so that they are all identical and add the Key col###
    amazon_toaster_df = post_processing_formatter.amazon_formatter(amazon_toaster_df)
    bestbuy_toaster_df = post_processing_formatter.bestbuy_formatter(bestbuy_toaster_df)
    walmart_toaster_df = post_processing_formatter.walmart_formatter(walmart_toaster_df)
    costco_toaster_df = post_processing_formatter.costco_formatter(costco_toaster_df)
    homedepot_toaster_df = post_processing_formatter.homedepot_formatter(homedepot_toaster_df)
    lowes_toaster_df = post_processing_formatter.lowes_formatter(lowes_toaster_df)
    
    # print(amazon_toaster_df)
    # print(bestbuy_toaster_df)
    # print(walmart_toaster_df)
    # print(costco_toaster_df)
    # print(homedepot_toaster_df)
    # print(lowes_toaster_df)
    
    
    ##############################################
    #                                            #
    #       PART THREE: COMBINE AND EXPORT       #
    #                                            #
    ##############################################
   
    list_of_stores = ["Amazon.com", "BestBuy.com", "Costco.com", "HomeDepot.com", "Lowes.com", "Walmart.com"]
    
    # combine all the df with the same appliance type
    combined_toaster_df = pd.concat([amazon_toaster_df, bestbuy_toaster_df, walmart_toaster_df, costco_toaster_df, homedepot_toaster_df, lowes_toaster_df], ignore_index=True)
    print(combined_toaster_df)
    # drop the duplicate rows
    combined_toaster_df.drop_duplicates()
    
    # filter out the reviews that are too old
    combined_toaster_df = combined_toaster_df[combined_toaster_df["review_date"] > n_days_ago]
    
    # map the reviews that appear on multiple sites to a single row in the dataframe
    combined_toaster_df = mapped_to_correct_stores.map_duped_reviews_to_shared_stores(combined_toaster_df, list_of_stores)
    
    # get rid of any cols starting with "Unnamed"
    combined_toaster_df = combined_toaster_df.loc[:, ~combined_toaster_df.columns.str.contains('^Unnamed')]
    print(combined_toaster_df)
    #export the df to excel
    combined_toaster_df.to_excel("outputs/Reviews/" + "Combined Slice Toaster Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    

if __name__ == "__main__":
    main()