# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
import json
import os
import sys

# 外部ライブラリ
import boto3
import pytest
from moto import mock_s3


# ------------------------------------------------------------------------------
# パス追加
# ------------------------------------------------------------------------------
sys.path.append('./src')

# ------------------------------------------------------------------------------
# S3に配置するファイル
# ------------------------------------------------------------------------------
PHONE_NUMBER_JSON = [
    {'start_day': 0, 'end_day': 0, 'phone_number': ['+11111111111', '+22222222222']},
    {'start_day': 1, 'end_day': 31, 'phone_number': ['+33333333333', '+44444444444']},
    {'start_day': 0, 'end_day': 0, 'phone_number': ['+55555555555', '+66666666666']}
]

MAPPING_GROUPS_JSON = [
    {
        "sns_topic_name": "a-topic",
        "phone_number_json_file": "a-phoneNumber.json"
    },
    {
        "sns_topic_name": "b-topic",
        "phone_number_json_file": "b-phoneNumber.json"
    }
]

B_PHONE_NUMBER_JSON = [
    {'start_day': 0, 'end_day': 0, 'phone_number': ['+11111111111', '+22222222222']},
    {'start_day': 0, 'end_day': 0, 'phone_number': ['+33333333333', '+44444444444']},
    {'start_day': 1, 'end_day': 31, 'phone_number': ['+55555555555', '+66666666666']}
]


# ------------------------------------------------------------------------------
# S3Bucket構築
# ------------------------------------------------------------------------------
@pytest.fixture
def s3():
    # テスト用環境変数設定
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['PHONE_NUMBER_BUCKET'] = 'my_bucket'
    os.environ['CONNECT_INSTANCE_ID'] = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    os.environ['CONNECT_CONTACT_FLOW_ID'] = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    os.environ['CONNECT_SOURCE_PHONE_NUMBER'] = '+10000000000'
    os.environ['CONNECT_ALARM_MSG'] = '大変なんです。'
    os.environ['CALL_REPEAT_COUNT'] = '2'
    os.environ['CALL_STATE_CHACK_INTERVAL_SECONDS'] = '10'

    with mock_s3():
        # mock用S3バケットの構築
        s3_bucket = os.getenv('PHONE_NUMBER_BUCKET')
        s3 = boto3.resource('s3')
        s3.create_bucket(Bucket=s3_bucket)

        # phoneNumber.jsonをS3に格納
        phone_number_obj = s3.Object(s3_bucket, 'phoneNumber.json')
        phone_number_obj.put(Body=json.dumps(PHONE_NUMBER_JSON))

        # mapping.jsonをS3に格納
        mapping_obj = s3.Object(s3_bucket, 'mapping.json')
        mapping_obj.put(Body=json.dumps(MAPPING_GROUPS_JSON))

        # b-phoneNumber.jsonをS3に格納
        mapping_obj = s3.Object(s3_bucket, 'b-phoneNumber.json')
        mapping_obj.put(Body=json.dumps(B_PHONE_NUMBER_JSON))

        yield
