import requests

def send_notify(mention_ids, message):
    """
    Microsoft Teamsに通知を送信する関数

    Args:
        mention_ids (list): メンションするIDのリスト
        message (str): 通知メッセージの本文

    Returns:
        bool: 通知が成功すればTrue、失敗すればFalse
    """

    # Webhook URLをベタ書きで指定
    webhook_url = "https://1966akioka.webhook.office.com/webhookb2/24ce70d8-1691-4b5e-aa90-67e8f56b36de@2f4ef158-134f-4faa-8db9-ef94be3b003a/IncomingWebhook/06ec01534f77477f9679950d30ee326e/2300d87e-df72-43f2-9367-9269f638e309/V2IJW5BzNLuCXyS-1pxN-7C7Kz4wq_zOJuSow6OIc6hWU1"

    # メンション部分を生成
    mentions = [
        {
            "type": "mention",
            "text": f"<at>{id}</at>",
            "mentioned": {
                "id": id,
                "name": id,
            }
        } for id in mention_ids
    ]

    # メンション用テキストを生成
    mention_text = ' '.join([f"@<at>{id}</at>" for id in mention_ids])

    # Adaptive Cardのペイロード
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": mention_text,
                            "color": "attention",
                            "size": "large",
                        },
                        {
                            "type": "TextBlock",
                            "text": "アキオカアプリからの通知です。",
                            "color": "default",
                            "size": "default",
                        },
                        {
                            "type": "TextBlock",
                            "text": message,
                            "color": "good",
                            "size": "medium",
                        },
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.0",
                    "msteams": {
                        "entities": mentions,
                    },
                },
            }
        ],
    }

    try:
        # HTTPリクエスト送信
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, json=payload, headers=headers)

        # レスポンスを確認
        if response.ok:
            print("通知が送信されました！")
            return True
        else:
            print(f"通知の送信に失敗しました。ステータスコード: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return False

    except requests.RequestException as e:
        print(f"リクエストエラー: {e}")
        return False
