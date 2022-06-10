# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from xmlrpc.client import boolean

# 外部ライブラリ
import boto3


# ------------------------------------------------------------------------------
# Class
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class AmazonConnect:
    instance_id: str
    contact_flow_id: str
    src_phone_number: str
    client: boto3.Session.client = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'client', boto3.client('connect', region_name='us-east-1'))

    def call(self, phone_number: str, msg: str, interval: int = 60) -> boolean:
        """
        電話をかけます

        Args:
            phone_number: 電話をかけたい番号
            msg: 電話で伝えたいメッセージ。2回繰り返し読み上げます
            interval: 発信してから電話に出たかを確認するまでのインターバル秒。デフォルト60秒

        Returns:
            True: 電話に応答した場合
            False: 電話に応答しなかった場合
        """
        call_response = self.client.start_outbound_voice_contact(
            InstanceId=self.instance_id,
            ContactFlowId=self.contact_flow_id,
            SourcePhoneNumber=self.src_phone_number,
            DestinationPhoneNumber=phone_number,
            Attributes={
                'message': msg + msg,
                'isTalking': 'false'
            }
        )

        contact_id = call_response['ContactId']

        time.sleep(interval)

        attributes = self.client.get_contact_attributes(
            InstanceId=self.instance_id,
            InitialContactId=contact_id
        )

        return bool(attributes['Attributes']['isTalking'] == 'true')

    def calls(self, phone_numbers: list[str], msg: str, interval: int = 60) -> boolean:
        """
        渡された電話番号のリストについて、並行処理で電話をかけます。

        Args:
            phone_numbers: 電話をかけたい番号のリスト
            msg: 電話で伝えたいメッセージ。2回繰り返し読み上げます
            interval: 発信してから電話に出たかを確認するまでのインターバル秒。

        Returns:
            True: 1人でも電話に応答した場合
            False: 誰も電話に応答しなかった場合
        """

        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="thread") as executor:

            call_results: list = []

            for phone_number in phone_numbers:
                # AmazonConnectから例外が返された場合 False 扱いにします
                try:
                    result = executor.submit(self.call, phone_number, msg, interval).result()
                except Exception:
                    call_results.append(False)
                else:
                    call_results.append(result)

        return True in call_results
