import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")


def delete_pdf_from_s3(pdf_key):
    """
    Deletes a PDF from an S3 bucket.

    Args:
        pdf_key (str): The key (path) of the PDF to delete from S3.
        bucket_name (str): The name of the S3 bucket.
        aws_access_key_id (str): AWS Access Key ID.
        aws_secret_access_key (str): AWS Secret Access Key.
    
    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    # Initialize the S3 client with provided AWS credentials
    s3 = boto3.client(
          's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
    )

    try:
        # Delete the PDF from the specified S3 bucket
        s3.delete_object(Bucket=aws_bucket_name, Key=pdf_key)
        return {"message": f'{pdf_key} deleted successfully from bucket {aws_bucket_name}'}
    
    except NoCredentialsError:
        return {"error": "AWS credentials are not available or invalid"}
    
    except ClientError as e:
        return {"error": f'Failed to delete PDF: {str(e)}'}

