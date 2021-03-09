import logging
import boto3
import os
from botocore.exceptions import ClientError

"static/waapp/css/*"
"static/waapp/css/style.css"


def create_presigned_url(object_name, expiration=300):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': os.environ['AWS_STORAGE_BUCKET_NAME'],
                                                       'Key': object_name},
                                               ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None
    return url
