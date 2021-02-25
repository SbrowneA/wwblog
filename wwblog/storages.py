from storages.backends.s3boto3 import S3Boto3Storage
import os


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
