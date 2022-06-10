# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
import json
from dataclasses import dataclass

# 外部ライブラリ
import boto3


# ------------------------------------------------------------------------------
# Class
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class DutyRepoS3:
    bucket_name: str
    region: str = 'us-east-1'

    def get_dict(self, s3_obj_key: str) -> dict:
        '''
        指定されたファイルをS3から取得し、dict型にして返します。
        '''
        s3 = boto3.resource('s3', region_name=self.region)
        s3_obj = s3.Object(self.bucket_name, s3_obj_key)
        body = s3_obj.get()['Body'].read()

        return json.loads(body.decode('utf8'))
