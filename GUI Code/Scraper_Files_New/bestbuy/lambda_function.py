from Scraper_Files_New.bestbuy import unwrangle_bestbuy_products
from Scraper_Files_New.bestbuy import unwrangle_bestbuy_reviews
def lambda_handler(event, context):
    
    search_term = event['search_term']
    api_key = event['api_key']
    destination_bucket = event['destination_bucket']
    days_ago = int(event['days_ago'])

    product_df = unwrangle_bestbuy_products.main(
        SEARCH_TERM=search_term, 
        API_KEY=api_key, 
        DESTINATION_BUCKET=destination_bucket
    )
    unwrangle_bestbuy_reviews.main(
        product_df=product_df, 
        API_KEY=api_key, 
        DESTINATION_BUCKET=destination_bucket, 
        DAYS_AGO=days_ago
    )