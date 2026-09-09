import os
import requests

bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

message = """🟢 Anime News Monitor

Telegram connection test successful!

The monitoring system is ready to receive official anime news.
"""

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": chat_id,
        "text": message
    }
)

print(response.status_code)
print(response.text)
