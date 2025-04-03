from Scraper_Files_New.costco import unwrangle_costco_products
from Scraper_Files_New.costco import unwrangle_costco_reviews
def lambda_handler(event, context):
    
    search_term = event['search_term']
    api_key = event['api_key']
    destination_bucket = event['destination_bucket']
    days_ago = int(event['days_ago'])

    product_df = unwrangle_costco_products.main(
        SEARCH_TERM=search_term, 
        API_KEY=api_key, 
        DESTINATION_BUCKET=destination_bucket
    )
    unwrangle_costco_reviews.main(
        product_df=product_df, 
        API_KEY=api_key, 
        REVIEW_DESTINATION_BUCKET=destination_bucket, 
        DAYS_AGO=days_ago
    )