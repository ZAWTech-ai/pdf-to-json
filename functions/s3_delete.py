import boto3
from botocore.exceptions import NoCredentialsError, ClientError

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
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    try:
        # Delete the PDF from the specified S3 bucket
        s3.delete_object(Bucket='edhubshop', Key=pdf_key)
        return {"message": f'{pdf_key} deleted successfully from bucket'}
    
    except NoCredentialsError:
        return {"error": "AWS credentials are not available or invalid"}
    
    except ClientError as e:
        return {"error": f'Failed to delete PDF: {str(e)}'}
