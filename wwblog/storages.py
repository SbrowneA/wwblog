from storages.backends.s3boto3 import S3Boto3Storage
import os


# TODO use this class in settings.py and place relevant AWS variables in this class
class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
