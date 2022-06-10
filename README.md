# Lambda Connect

Amazon Connectを使用し、指定された電話番号へ電話をかけアラートメッセージを読み上げます。

## 要件(ユーザーストーリー)

|だれが|何をしたい|それはなぜか|実装Status|
|:--|:--|:--|:--:|
|プロダクトオーナー|障害時、当番の人にコールしたい。|障害にすぐ気づいて復旧してほしいため。|✅|
|保守リーダー|障害が発生した案件ごとにコール先(当番表)を分けてほしい。|案件毎に担当者が違う可能性があり、かつ複数案件が1つのAWSアカウント内にある場合もある。関係無い人にコールをしたくないため。|未|
|保守リーダー|障害が発生した案件ごとにアラートメッセージを分けてほしい|案件毎に担当者が違う可能性があり、かつ複数案件が1つのAWSアカウント内にある場合もある。案件毎に適切なアラートメッセージを伝えたいため。|未|
|保守リーダー|日付によって当番を変えてほしい。|毎日障害コールがかかってくると、心身共に疲弊してしまうため。|✅|
|保守リーダーA|当番がコールに出なかったら次の順番の当番にコールしてほしい。|当番が寝ていて起きれなかった場合でも誰かしらで対応したいため。|✅|
|保守リーダーB|当番がコールに出なかったら繰り返しその当番にコールしてほしい。|自分の当番日以外はコールは無いという安心感がほしいため。|✅|
|保守リーダーB|当番は複数人設定したい。|複数人で障害対応にあたりたいため。当番を複数人にすることで、誰も電話にでれない可能性を減らしたいため。|✅|
|当番メンテナー|プログラムを変更せずに当番を変更したい。|当番は変更頻度が高いが、そのたびにプログラムリリースするのは面倒なため。|✅|
|当番メンテナー|当番変更後に、コールはしないテストをしたい。|当番変更作業にミスがないか確認するため。実際にコールが発生すると当番に迷惑がかかるため。|未|

## 想定構成図

### simpleモード

1つのAWSアカウント内で、当番表が1つで済み場合。

![simple](./assets/simple.dio.svg)

### mappingモード

1つのAWSアカウント内に複数案件があり、案件ごとに当番表を分けたい場合。

![mapping](./assets/mapping.dio.svg)

マッピングファイルを用いると、SNSTopic名と当番表ファイルの紐付けが可能なので、
案件ごとにLambdaやAmazonConnectを作らなくて済みます。


## 前提条件


- AmazonConnectの設定が完了していること

### S3

電話番号情報ファイルを格納するS3が存在すること

### 当番表(PHONE_NUMBER_JSON_FILE)

コール先の電話番号情報を定義する必要があります。jsonファイルとしてS3バケットに格納してください。

|Name|Type|Requierd|Description|ex|
|:--|:--:|:--:|:--|:--|
|-|`array of object`|yes|このJsonは配列から始まります。|-|
|&emsp;`startDay`|`number`|yes|電話対応ローテーションの開始日|`1`|
|&emsp;`endDay`|`number`|yes|電話対応ローテーションの終了日|`15`|
|&emsp;`phoneNumber`|`array of string`|yes|対応者の電話番号|`["+1111111111", "+2222222222"]`|

例: [phoneNumber.json](./samlejson/../samplejson/phoneNumber.json)

なお、旧フォーマットも対応しています。

|項目|タイプ|説明|例|
|:--|:--:|:--|:--|
|`groupX`|`map`|電話対応のグループ、命名は必ずこの通りに従ってください。|`group1`, `group2`|
|`start_day`|`number`|電話対応ローテーションの開始日|`1`|
|`end_day`|`number`|電話対応ローテーションの終了日|`15`|
|`phone_number`|`list(string)`|対応者の電話番号|`["+1111111111", "+2222222222"]`||

例: [phoneNumber_old.json](./samplejson/phoneNumber_old.json)

### マッピングファイル

SNSTopicと当番表ファイルの紐付け一覧です。
案件(SNSTopic)毎に違う当番表を使用したい場合、マッピングファイルが必要になります。

|Name|Type|Required|Description|例|
|:--|:--:|:--:|:--|:--|
|-|`array of object`|yes|このJsonは配列から始まります。|-|
|&emsp;`snsTopicName`|`string`|yes|AWSのSNSTopic名|`projectA-sns-topic`|
|&emsp;`phoneNumberJsonFile`|`string`|yes|参照する当番表ファイルのパス|`projectA-phoneNumber.json`|

例: [mapping.json](./samplejson/mapping.json)



### AmazonConnect

### IAM Policy


Lambdaに以下の権限を付与する必要があります。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:List*",
        "s3:Get*"
      ],
      "Resource": [
        "${s3_bucket_arn}",
        "${s3_bucket_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "connect:StartOutboundVoiceContact",
        "connect:GetContactAttributes",
        "connect:StopContact"
      ],
      "Resource": [
       "arn:aws:connect:${region}:${account_id}:instance/${instance_id}/*"
      ]
    }
  ]
}
```

## 必要なファイル


## event

Amazon SNS メッセージイベントは以下の参照してください。

[Amazon SNS でのAWS Lambdaの使用](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/with-sns.html)

当Lambdaでは、案件(SNSTopic)毎に違う当番表を使用したい場合にのみ、イベント情報のTopicArnが必要になります。

## returns

`None`

## 環境変数

|Parameter|Description|Defaualt|Required|
|:--|:--|:--|:--:|
|`CALL_REPEAT_COUNT`|繰り返し回数|`3`|no|
|`CALL_REPEAT_GROUP`|担当日の当番へ繰り返しコールする<br>  - True: 繰り返す<br>  - False：次の当番へコールする|`False`|no|
|`CALL_STATE_CHACK_INTERVAL_SECONDS`|発信してから、電話に出たかを確認するまでのインターバル(秒)|`60`|no|
|`CONNECT_ALARM_MSG`|AmazonConnectが読み上げるメッセージ|`障害が発生しました。`|no|
|`CONNECT_CONTACT_FLOW_ID`|AmazonConnectコンタクトフローID|-|yes|
|`CONNECT_EXTRA_DESTINATION_PHONE_NUMBER`|全てのグループを確認したが<br>日付が一致しなかった場合に電話する番号|-|yes|
|`CONNECT_INSTANCE_ID`|AamzonConnectインスタンスID|-|yes|
|`CONNECT_SOURCE_PHONE_NUMBER`|AmazonConnect発信元電話番号|-|yes|
|`PHONE_NUMBER_BUCKET`|当番表が配置されているS3バケット名|-|yes|
|`PHONE_NUMBER_JSON_FILE`|当番表のオブジェクト名|`phoneNumber.json`|yes|
|`MAPPING_JSON_FILE`|SNSTopicと当番表ファイルの紐付け一覧|-|no|












# ローカルテスト
## 環境変数の設定
上記 環境環境 を参考に、それぞれの環境に合わせて `docker-compose.yamlのenvironment`及びを修正、`.env`ファイルを作成します。

### .env のサンプル
```conf
CONNECT_ALARM_MSG=XXシステムで障害が発生しました。詳しくはSlackを確認してください。
CONNECT_CONTACT_FLOW_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CONNECT_EXTRA_DESTINATION_PHONE_NUMBER=+81xxxxxxxxxx
CONNECT_INSTANCE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CONNECT_SOURCE_PHONE_NUMBER=+81xxxxxxxxxx
PHONE_NUMBER_BUCKET=xx-connect-s3
```

## コンテナ起動
```bash
docker-compose up
```

## リクエスト
```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```


# Licence
MIT