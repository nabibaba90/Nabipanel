from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 17570480
api_hash = '18c5be05094b146ef29b0cb6f6601f1f'

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Oturum anahtarınız (String Session):")
    print(client.session.save())
