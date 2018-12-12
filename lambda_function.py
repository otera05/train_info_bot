import requests
import os, json
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, Formatter


# ログ出力設定
logger = getLogger(__name__)
formatter = Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

# 環境変数初期化
URL = 'https://rti-giken.jp/fhc/api/train_tetsudo/delay.json'
ROUTES = ['中央･総武各駅停車', '中央線快速電車', '大江戸線', '京王線', '西武新宿線']
WEBHOOK_URL = 'https://hooks.slack.com/services/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'

# Lambda
URL = os.environ['URL']
ROUTES = os.environ['ROUTES']
WEBHOOK_URL = os.environ['WEBHOOK_URL']


def create_body():
    try:
        msg = 'APIアクセス処理：APIにアクセスします。'
        logger.debug(msg)
        res = requests.get(URL)
        if res.status_code == 200:
            results = res.json()

            msg = '遅延情報成形処理：フラグと変数を初期化します。'
            logger.debug(msg)

            delay_flag = False
            delay_info =[]
            dt = datetime.now().strftime('%H:%M:%S')
            text = ''
            
            msg = '遅延情報成形処理：成形を開始します。'
            logger.debug(msg)

            for result in results:
                for route in ROUTES:
                    if route in result['name']:
                        delay_flag = True
                        msg = '{0} 時点の運行状況：{1}で遅延しています。'.format(dt, route)
                        delay_info.append(msg)
                    else:
                        continue

            if delay_flag:
                for info in delay_info:
                    text += info + '\n'

            else:
                text = '遅延情報はありません。'
            
            msg = '遅延情報成形処理：成形が完了しました。'
        
        else:
            msg = 'APIアクセス処理エラー：ステータスコード：%s' % res.status_code
            logger.debug(msg)

    except requests.exceptions.RequestException as e:
        text = 'APIアクセス処理エラー：遅延情報APIへのアクセス時に例外が発生しました。メッセージ：%s' % e
        logger.debug(text)
    
    return text

def post_to_slack(text):
    payload = {
        'text': text
    }
    
    msg = 'Slack処理：SlackにメッセージをPOSTします。'
    logger.debug(msg)

    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code == 200:
        msg = 'Slack処理：SlackへのPOSTが正常に終了しました。'
        logger.debug(msg)

    else:
        msg = 'Slack処理：ステータスコード：%s' % res.status_code
        logger.debug(msg)


def lambda_handler(event, context):
    text = create_body()
    post_to_slack(text)

    return {
        'status_code': 200,
        'text': '正常に終了しました。'
    }
