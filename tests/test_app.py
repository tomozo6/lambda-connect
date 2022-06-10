# ------------------------------------------------------------------------------
# メモ
# ------------------------------------------------------------------------------
# - S3はmockを使用。
# - AmazonConnectは繋がらない。
#    (s3でmockを使用しているのでクルデンシャルがバグる。
#     ただテスト時に繋がらないのは好都合なのでそのままにしている)
# - ログ出力内容をassertで確認するようにした。
# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
import logging
import os

# ローカルライブラリ
from app import alert_call_scenario


# ------------------------------------------------------------------------------
# SNS Event
# ------------------------------------------------------------------------------
SNS_EVENT = {
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:lambda_topic:0b6941c3-f04d-4d3e-a66d-b1df00e1e381",
            "Sns": {
                "Type": "Notification",
                "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                "TopicArn": "arn:aws:sns:us-east-1:123456789012:b-topic",
                "Subject": "TestInvoke",
                "Message": "<message payload>",
                "Timestamp": "2015-04-02T07:36:57.451Z",
                "SignatureVersion": "1",
                "Signature": "r0Dc5YVHuAglGcmZ9Q7SpFb2PuRDFmJNprJlAEEk8CzSq9Btu8U7dxOu++uU",
                "SigningCertUrl": "http://sns.us-east-1.amazonaws.com/SimpleNotificationService-d6d679a1d18e95c2f9ffcf11f4f9e198.pem",
                "UnsubscribeUrl": "http://cloudcast.amazon.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:123456789012:example_topic:0b6941c3-f04d-4d3e-a66d-b1df00e1e381",
                "MessageAttributes": {"key": {"Type": "String", "Value": "value"}}
            }
        }
    ]
}


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
class TestAlertCallScenario:
    def test_simple_mode(self, s3, caplog):
        # テスト用環境変数展開
        del os.environ['MAPPING_JSON_FILE']
        os.environ['CALL_REPEAT_GROUP'] = 'False'

        # テスト対象関数実行
        alert_call_scenario(SNS_EVENT)

        want_log_tuples = [
            ('root', logging.INFO, 'SimpleMode.'),
            ('root', logging.INFO, 'Get phoneNumberJsonFile: phoneNumber.json'),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.INFO, "Call ['+55555555555', '+66666666666']."),
            ('root', logging.INFO, "Call ['+11111111111', '+22222222222']."),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.INFO, "Call ['+55555555555', '+66666666666']."),
            ('root', logging.INFO, "Call ['+11111111111', '+22222222222']."),
            ('root', logging.ERROR, 'No one answered the phone.'),
        ]

        assert want_log_tuples == caplog.record_tuples

    def test_mapping_mode(self, s3, caplog):
        # テスト用環境変数展開
        os.environ['MAPPING_JSON_FILE'] = 'mapping.json'
        os.environ['CALL_REPEAT_GROUP'] = 'False'

        # テスト対象関数実行
        alert_call_scenario(SNS_EVENT)

        want_log_tuples = [
            ('root', logging.INFO, 'MappingMode.'),
            ('root', logging.INFO, 'Get mappingJsonFile: mapping.json'),
            ('root', logging.INFO, 'Get phoneNumberJsonFile: b-phoneNumber.json'),
            ('root', logging.INFO, "Call ['+55555555555', '+66666666666']."),
            ('root', logging.INFO, "Call ['+11111111111', '+22222222222']."),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.INFO, "Call ['+55555555555', '+66666666666']."),
            ('root', logging.INFO, "Call ['+11111111111', '+22222222222']."),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.ERROR, 'No one answered the phone.'),
        ]

        assert want_log_tuples == caplog.record_tuples

    def test_repeat_group_mode(self, s3, caplog):
        # テスト用環境変数展開
        del os.environ['MAPPING_JSON_FILE']
        os.environ['CALL_REPEAT_GROUP'] = 'True'

        alert_call_scenario(SNS_EVENT)

        want_log_tuples = [
            ('root', logging.INFO, 'SimpleMode.'),
            ('root', logging.INFO, 'Get phoneNumberJsonFile: phoneNumber.json'),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.INFO, "Call ['+33333333333', '+44444444444']."),
            ('root', logging.ERROR, 'No one answered the phone.'),
        ]

        assert want_log_tuples == caplog.record_tuples
