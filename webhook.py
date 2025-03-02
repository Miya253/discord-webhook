import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/ID/TOKEN"

data = {
    "content": "message"
}

response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("✅ 訊息發送成功！")
else:
    print(f"❌ 發送失敗，狀態碼: {response.status_code}, 回應: {response.text}")