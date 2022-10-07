from datetime import datetime
import os
import dotenv
import boto3
from typing import List

dotenv.load_dotenv()
AWS_ACCESS_KEY = os.getenv('aws_access_key_id', "")
AWS_SECRET_KEY = os.getenv("aws_secret_access_key", "")
S3_BUCKET_NAME = os.getenv("bucket", "")
ARCHIVE_DIRS = os.getenv("archives", "archives")

class S3File:
    def __init__(self, file: str, date: datetime):
        self.name = file
        self.date = date
        self.s3_client = s3_client

    def remove(self):
        self.s3_client.delete_object(self.name)

    def get_date(self):
        return f"{self.date.year}-{self.date.month}"


class MyS3Client:
    def __init__(self, access_key: str, secret_key: str, bucket_name: str):
        boto3_s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.s3_client = boto3_s3
        self.bucket_name = bucket_name

    def get_files(self, folder: str) -> List[S3File]:
        files = self.s3_client.list_objects(
            Bucket=self.bucket_name, Prefix=folder)
        file_list: List[S3File] = []
        if files.get("Contents"):
            for file in files['Contents']:
                key = file.get("Key")
                date = file.get('LastModified')
                if key and date:
                    file_list.append(S3File(key, date))
            return file_list
        return file_list

    def delete_object(self, file: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=file)

    def upload(self, file, file_path) -> S3File:
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            file_path,
            # ExtraArgs=extra_args
        )
        return S3File(file=file_path, date=datetime.now())


# MyS3Client instance
s3_client = MyS3Client(AWS_ACCESS_KEY, AWS_SECRET_KEY,
                       S3_BUCKET_NAME)
