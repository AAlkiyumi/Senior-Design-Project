import unwrangle_amazon_products
import unwrangle_amazon_reviews
def lambda_handler(event, context):

    api_key = event['api_key']
    search_term = event['search_term']
    destination_bucket = event['destination_bucket']
    cookie = event['cookie']
    days_ago = int(event['days_ago'])

    product_df = unwrangle_amazon_products.main(
        SEARCH_TERM=search_term, 
        API_KEY=api_key, 
        DESTINATION_BUCKET=destination_bucket
    )
    unwrangle_amazon_reviews.main(
        product_df=product_df, 
        API_KEY=api_key, 
        DESTINATION_BUCKET=destination_bucket, 
        DAYS_AGO=days_ago, 
        COOKIE=cookie
    )