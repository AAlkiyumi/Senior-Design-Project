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
    mandatory_slow_cooker_href_list = [
        ]
           
    # """
    print("Scraping Amazon.com Reviews...")
    # amazon_slow_cooker_df = amazon2.main(["https://www.amazon.com/s?k=slow+cooker&page=", "&crid=3K2FU617MMNBP&qid=1712857427&sprefix=slow+cooker%2Caps%2C139&ref=sr_pg_"], "Slow Cooker", 20, mandatory_slow_cooker_href_list, n_days_ago)
      
    ### Scrape BestBuy.com Reviews ### Perfect
    print("Scraping BestBuy.com Reviews...")
    # bestbuy_slow_cooker_df = bestbuy2.main(["https://www.bestbuy.com/site/searchpage.jsp?st=slow+cooker&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page", "&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"], "Slow Cooker", 1, n_days_ago)

    
    ### Scrape Walmart.com Reviews ### Perfect
    print("Scraping Walmart.com Reviews...")
    # walmart_slow_cooker_df = walmart2.main("https://www.walmart.com/search?q=slow+cooker&facet=retailer_type%3AWalmart&page=", "Slow Cooker", 6, n_days_ago)


    #The following use selenium, ensure vpn is turned on
    #input("Ensure you are connected to VPN to avoid getting blocked. Press Enter to continue...")

    
    ### Scrape Costco.com Reviews ### Perfect
    print("Scraping Costco.com Reviews...")
    # costco_slow_cooker_df = costco_selenium.main("https://www.costco.com/pressure-slow-cookers.html", 1, "Slow Cooker", 0) # Already included in pressure cooker reviews
    """
    """
    ### Scrape HomeDepot.com Reviews ### Perfect
    print("Scraping HomeDepot.com Reviews...")
    # homedepot_slow_cooker_df = homedepot_selenium.main("Slow Cooker", n_days_ago, 20, "https://www.homedepot.com/b/Appliances-Small-Kitchen-Appliances-Cookers-Slow-Cookers/N-5yc1vZc68r?NCNI-5&searchRedirect=slow%20cooker&semanticToken=i10r20200f22000000000e_202404111749165642982204374_us-central1-89jm%20i10r20200f22000000000e%20%3E%20rid%3A%7Beca40b07225e3f8c64b5f9954743ab6c%7D%3Arid%20st%3A%7Bslow%20cooker%7D%3Ast%20ml%3A%7B24%7D%3Aml%20pt%3A%7Bslow%20cooker%7D%3Apt%20nr%3A%7Bslow%20cooker%7D%3Anr%20nf%3A%7Bn%2Fa%7D%3Anf%20qu%3A%7Bslow%20cooker%7D%3Aqu%20ie%3A%7B0%7D%3Aie%20qr%3A%7Bslow%20cooker%7D%3Aqr")
    
    
    ### Scrape Lowes.com Reviews ### Perfect
    print("Scraping Lowes.com Reviews...")
    # lowes_slow_cooker_df = lowes_selenium.main("https://www.lowes.com/search?searchTerm=slow+cooker", 4, "Slow Cooker", n_days_ago)
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
    
    amazon_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Amazon.com Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    bestbuy_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\BestBuy.com Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    walmart_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Walmart.com Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    # costco_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Costco.com Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    homedepot_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Homedepot Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    lowes_slow_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Lowes.com Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    
    ############################################################################################


    ### Now that we've scraped all the reviews, format the dataframes so that they are all identical and add the Key col###
    amazon_slow_cooker_df = post_processing_formatter.amazon_formatter(amazon_slow_cooker_df)
    bestbuy_slow_cooker_df = post_processing_formatter.bestbuy_formatter(bestbuy_slow_cooker_df)
    walmart_slow_cooker_df = post_processing_formatter.walmart_formatter(walmart_slow_cooker_df)
    # costco_slow_cooker_df = post_processing_formatter.costco_formatter(costco_slow_cooker_df)
    homedepot_slow_cooker_df = post_processing_formatter.homedepot_formatter(homedepot_slow_cooker_df)
    lowes_slow_cooker_df = post_processing_formatter.lowes_formatter(lowes_slow_cooker_df)
    
    # print(amazon_slow_cooker_df)
    # print(bestbuy_slow_cooker_df)
    # print(walmart_slow_cooker_df)
    # print(costco_slow_cooker_df)
    # print(homedepot_slow_cooker_df)
    # print(lowes_slow_cooker_df)
    
    
    ##############################################
    #                                            #
    #       PART THREE: COMBINE AND EXPORT       #
    #                                            #
    ##############################################
   
    list_of_stores = ["Amazon.com", "BestBuy.com", "Walmart.com", "Homedepot.com", "Lowes.com"]
    
    # combine all the df with the same appliance type
    combined_slow_cooker_df = pd.concat([amazon_slow_cooker_df, bestbuy_slow_cooker_df, walmart_slow_cooker_df], ignore_index=True)
    print(combined_slow_cooker_df)
    # drop the duplicate rows
    combined_slow_cooker_df.drop_duplicates()
    
    # filter out the reviews that are too old
    combined_slow_cooker_df = combined_slow_cooker_df[combined_slow_cooker_df["review_date"] > n_days_ago]
    
    # map the reviews that appear on multiple sites to a single row in the dataframe
    combined_slow_cooker_df = mapped_to_correct_stores.map_duped_reviews_to_shared_stores(combined_slow_cooker_df, list_of_stores)
    
    # get rid of any cols starting with "Unnamed"
    combined_slow_cooker_df = combined_slow_cooker_df.loc[:, ~combined_slow_cooker_df.columns.str.contains('^Unnamed')]
    print(combined_slow_cooker_df)
    #export the df to excel
    combined_slow_cooker_df.to_excel("outputs/Reviews/" + "Combined Slow Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    

if __name__ == "__main__":
    main()