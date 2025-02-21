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
    mandatory_cooker_href_list = [
        ]
           
    """
    print("Scraping Amazon.com Reviews...")
    amazon_cooker_df = amazon2.main(["https://www.amazon.com/s?k=multi+cooker&page=", "&crid=3LORPVGWZ8PO&qid=1712670484&sprefix=multi+cooker%2Caps%2C250&ref=sr_pg_"], "Multi Cooker", 10, mandatory_cooker_href_list, n_days_ago)
      
    ### Scrape BestBuy.com Reviews ### Perfect
    print("Scraping BestBuy.com Reviews...")
    bestbuy_cooker_df = bestbuy2.main(["https://www.bestbuy.com/site/searchpage.jsp?cp=", "&id=pcat17071&st=multi+cooker"], "Multi Cooker", 2, n_days_ago)

    
    ### Scrape Walmart.com Reviews ### Perfect
    print("Scraping Walmart.com Reviews...")
    walmart_cooker_df = walmart2.main("https://www.walmart.com/search?q=multi+cooker&page=", "Multi Cooker", 10, n_days_ago)


    #The following use selenium, ensure vpn is turned on
    #input("Ensure you are connected to VPN to avoid getting blocked. Press Enter to continue...")

    
    ### Scrape Costco.com Reviews ### Perfect
    print("Scraping Costco.com Reviews...")
    costco_cooker_df = costco_selenium.main("https://www.costco.com/CatalogSearch?dept=All&keyword=multi+cooker", 1, "Multi Cooker", 0)
    """
    """
    ### Scrape HomeDepot.com Reviews ### Perfect
    print("Scraping HomeDepot.com Reviews...")
    # homedepot_cooker_df = homedepot_selenium.main("Multi Cooker", n_days_ago, 20, "https://www.homedepot.com/b/Appliances-Small-Kitchen-Appliances-cooker-Makers/N-5yc1vZbv4w?NCNI-5&searchRedirect=cooker%20maker&semanticToken=i10r20200f220000000000_2024021217001498788913073828_us-east4-ls5k%20i10r20200f220000000000%20%3E%20rid%3A%7B4ed60789ea72b2836dc03469ecaf06bf%7D%3Arid%20st%3A%7Bcooker%20maker%7D%3Ast%20ml%3A%7B24%7D%3Aml%20pt%3A%7Bcooker%20maker%7D%3Apt%20nr%3A%7Bcooker%20maker%7D%3Anr%20nf%3A%7Bn%2Fa%7D%3Anf%20qu%3A%7Bcooker%20maker%7D%3Aqu%20ie%3A%7B0%7D%3Aie%20qr%3A%7Bcooker%20maker%7D%3Aqr")
    
    
    ### Scrape Lowes.com Reviews ### Perfect
    print("Scraping Lowes.com Reviews...")
    # lowes_cooker_df = lowes_selenium.main("https://www.lowes.com/search?searchTerm=cooker%20maker", 4, "Multi Cooker", n_days_ago)
    """

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
    
    amazon_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Amazon.com Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    bestbuy_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\BestBuy.com Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    walmart_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Walmart.com Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    costco_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Costco.com Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    # homedepot_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Homedepot Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    # lowes_cooker_df = excelSheetToDf(r"C:\Users\sdacoop2\OneDrive - Midea America Corp\Documents\GitHub\web-scraping-sentiment-analysis-new\SDA\outputs\Reviews\Lowes.com Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", "Sheet1")
    
    ############################################################################################


    ### Now that we've scraped all the reviews, format the dataframes so that they are all identical and add the Key col###
    amazon_cooker_df = post_processing_formatter.amazon_formatter(amazon_cooker_df)
    bestbuy_cooker_df = post_processing_formatter.bestbuy_formatter(bestbuy_cooker_df)
    walmart_cooker_df = post_processing_formatter.walmart_formatter(walmart_cooker_df)
    costco_cooker_df = post_processing_formatter.costco_formatter(costco_cooker_df)
    # homedepot_cooker_df = post_processing_formatter.homedepot_formatter(homedepot_cooker_df)
    # lowes_cooker_df = post_processing_formatter.lowes_formatter(lowes_cooker_df)
    
    # print(amazon_cooker_df)
    # print(bestbuy_cooker_df)
    # print(walmart_cooker_df)
    # print(costco_cooker_df)
    # print(homedepot_cooker_df)
    # print(lowes_cooker_df)
    
    
    ##############################################
    #                                            #
    #       PART THREE: COMBINE AND EXPORT       #
    #                                            #
    ##############################################
   
    list_of_stores = ["Amazon.com", "BestBuy.com", "Costco.com", "Walmart.com"]
    
    # combine all the df with the same appliance type
    combined_cooker_df = pd.concat([amazon_cooker_df, bestbuy_cooker_df, walmart_cooker_df, costco_cooker_df], ignore_index=True)
    print(combined_cooker_df)
    # drop the duplicate rows
    combined_cooker_df.drop_duplicates()
    """
    # filter out the reviews that are too old
    combined_cooker_df = combined_cooker_df[combined_cooker_df["review_date"] > n_days_ago]
    
    # map the reviews that appear on multiple sites to a single row in the dataframe
    combined_cooker_df = mapped_to_correct_stores.map_duped_reviews_to_shared_stores(combined_cooker_df, list_of_stores)
    """
    # get rid of any cols starting with "Unnamed"
    combined_cooker_df = combined_cooker_df.loc[:, ~combined_cooker_df.columns.str.contains('^Unnamed')]
    print(combined_cooker_df)
    #export the df to excel
    combined_cooker_df.to_excel("outputs/Reviews/" + "Combined Multi Cooker Reviews " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx", index=False)
    

if __name__ == "__main__":
    main()