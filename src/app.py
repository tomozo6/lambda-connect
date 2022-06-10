# ------------------------------------------------------------------------------
# Import Library
# ------------------------------------------------------------------------------
# 標準ライブラリ
import itertools
import json
import logging
import os
from xmlrpc.client import boolean

# 外部ライブラリ
#from dotenv import load_dotenv

# ローカルライブラリ
from mypkg.duty import (
    DutyRepoS3,
    make_duty_groups,
    make_duty_roster,
    make_mapping_groups
)
from mypkg.call import AmazonConnect

# ------------------------------------------------------------------------------
# 前処理
# ------------------------------------------------------------------------------
# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ------------------------------------------------------------------------------
# Function
# ------------------------------------------------------------------------------
def alert_call_scenario(event):
    # --------------------------------------------------------------------
    # 0. 環境変数の設定
    # --------------------------------------------------------------------
    try:
        # DutyRope
        S3_BUCKET_NAME = os.environ['PHONE_NUMBER_BUCKET']
        phone_number_json_file = os.getenv('PHONE_NUMBER_JSON_FILE', 'phoneNumber.json')
        MAPPING_JSON_FILE = os.getenv('MAPPING_JSON_FILE', None)

        # AmazonConnect
        SOURCE_PHONE_NUMBER = os.environ['CONNECT_SOURCE_PHONE_NUMBER']
        INSTANCE_ID = os.environ['CONNECT_INSTANCE_ID']
        CONTACT_FLOW_ID = os.environ['CONNECT_CONTACT_FLOW_ID']
        CONNECT_ALARM_MSG = os.getenv(
            'CONNECT_ALARM_MSG',
            '障害が発生しました。'
        )

        # CALL
        CALL_REPEAT_GROUP: boolean = eval(os.getenv('CALL_REPEAT_GROUP', 'False'))
        CALL_REPEAT_COUNT: int = int(os.getenv('CALL_REPEAT_COUNT', 3))
        CALL_STATE_CHACK_INTERVAL_SECONDS: int = int(os.getenv(
            'CALL_STATE_CHACK_INTERVAL_SECONDS', 60))

    except Exception as e:
        logger.error('Failed to set environment variables.')
        raise e

    # --------------------------------------------------------------------
    # 1. DutyGroupsの作成
    # --------------------------------------------------------------------
    repo = DutyRepoS3(S3_BUCKET_NAME)

    # マッピングモード判定
    if MAPPING_JSON_FILE is None:
        logger.info('SimpleMode.')
    else:
        logger.info('MappingMode.')
        logger.info(f'Get mappingJsonFile: {MAPPING_JSON_FILE}')
        mapping_groups_dict = repo.get_dict(MAPPING_JSON_FILE)
        mapping_groups = make_mapping_groups(mapping_groups_dict)
        # マッピング先のJsonファイル名で、変数phone_number_json_fileを上書きする。
        sns_topic_name = str(event['Records'][0]['Sns']['TopicArn']).split(':')[-1]
        phone_number_json_file = mapping_groups.get_phone_number_json_file(sns_topic_name)

    logger.info(f'Get phoneNumberJsonFile: {phone_number_json_file}')
    duty_groups_dict = repo.get_dict(phone_number_json_file)
    duty_groups = make_duty_groups(duty_groups_dict)

    # --------------------------------------------------------------------
    # 2. DutyRosterの作成(今日の日付を考慮したコール当番表を作成する)
    # --------------------------------------------------------------------
    duty_roster = make_duty_roster(duty_groups, CALL_REPEAT_COUNT, CALL_REPEAT_GROUP)

    # --------------------------------------------------------------------
    # 3. 電話(AmazonConnect)の設定をする
    # --------------------------------------------------------------------
    amazon_connect = AmazonConnect(INSTANCE_ID, CONTACT_FLOW_ID, SOURCE_PHONE_NUMBER)

    # --------------------------------------------------------------------
    # 4. 電話する
    # --------------------------------------------------------------------
    # 単純にi番目に電話すべき番号リストを取得して単純に電話しているだけ。
    for i in itertools.count():
        # 当番表オブジェクトから、i番目に電話すべき番号リストを取得
        phone_numbers = duty_roster.get_duty_phone_numbers(i)

        # 全ての順番に電話し終えたらエラーログを出してループを終える。
        # (誰も電話に出なかったということ)
        if phone_numbers is None:
            logger.error('No one answered the phone.')
            break

        # 取得した番号リストに電話する
        logger.info(f'Call {phone_numbers}.')
        is_answer = amazon_connect.calls(
            phone_numbers,
            CONNECT_ALARM_MSG,
            CALL_STATE_CHACK_INTERVAL_SECONDS
        )

        # 誰かが電話に出たらループを終える。
        if is_answer:
            logger.info('Someone in the group answered the phone.')
            break


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def handler(event, context) -> None:
    logging.info('Start function.')
    logger.info('Event: {}'.format(json.dumps(event)))

    logging.info('Start alert call scenario.')
    alert_call_scenario(event)
    logging.info('End alert call scenario.')

    logger.info('End function.')


#if __name__ == "__main__":
#    # テスト用に環境変数の展開
##    load_dotenv()
#    handler('dummy', 'dummy')
