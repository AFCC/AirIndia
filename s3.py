from boto3 import Session
from config import s3_creds

class S3:
    def __init__(self) -> None:
        self.ACCESS_KEY = s3_creds["access_key"]
        self.SECRET_KEY = s3_creds["secret_key"]
        self.REGION_NAME = s3_creds["region"]
        self.BUCKET_NAME = s3_creds["bucket"]

        self.ses = Session(aws_access_key_id=self.ACCESS_KEY,
                    aws_secret_access_key=self.SECRET_KEY,
                    region_name=self.REGION_NAME)

    def upload(self, local_file_name, remote_file_name):
        self.key = remote_file_name
        self.content_type = 'application/pdf'
        self.s3 = self.ses.resource('s3')

        self.s3.Bucket(self.BUCKET_NAME).put_object(Key=self.key, Body=open(local_file_name, 'rb'), ContentType=self.content_type)

    def get_link(self, key):
        try:
            self.s3.Object(self.BUCKET_NAME, key).load()

        except Exception as e:
            print(f"Error# Fetching link | {str(e)}")
            return ''

        else:
            url = self.ses.client('s3').generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.BUCKET_NAME,
                    'Key': key,
                    # 'ResponseContentDisposition': 'attachment'
                },
                ExpiresIn=604800)
        return url