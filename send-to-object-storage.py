import os
import boto3

bucket_name = "roya-data-eng-20250610"
directory = "./stage"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "eu-central-1"),
)

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)

    if os.path.isfile(file_path):
        s3.upload_file(file_path, bucket_name, filename)
        print(f"{filename} uploaded successfully")