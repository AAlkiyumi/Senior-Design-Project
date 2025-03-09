import boto3
import pandas as pd
import io


# Specify your S3 bucket and file key (filename)
# bucket_name = "your-bucket-name"
# file_key = "your-folder/sample.csv"  # Adjust path if in a folder
def read_csv_from_s3(bucket_name, file_key):
    # S3 client
    s3 = boto3.client("s3")

    try:
        # Fetch file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        
        # Read CSV file content into Pandas DataFrame
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_data))
        
        return df

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()
    
def save_csv_to_s3(bucket_name: str, s3_key: str, df: pd.DataFrame):
    """
    Saves a Pandas DataFrame as a CSV file to an S3 bucket.

    :param bucket_name: str - Name of the S3 bucket
    :param s3_key: str - Path/key for the file in S3 (e.g., "folder/filename.csv")
    :param df: pd.DataFrame - The DataFrame to save
    """
    
    # Convert DataFrame to CSV and store in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Initialize S3 client
    s3 = boto3.client("s3")

    try:
        # Upload CSV to S3
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())

        print(f"File '{s3_key}' saved successfully to bucket '{bucket_name}'")
        return {"statusCode": 200, "body": f"File '{s3_key}' saved successfully"}

    except Exception as e:
        print(f"Error saving file to S3: {e}")
        return {"statusCode": 500, "body": str(e)}