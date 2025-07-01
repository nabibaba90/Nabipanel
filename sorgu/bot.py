import asyncio
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Telegram API bilgileri
api_id = 24396967
api_hash = '7ddf52c9da17c98550cb937552ebffb8'
string_session = "1ApWapzMBuzs9njNDBHSqIOUiOdyn1y94Q3V-83VeoMC_uWXUo1K_ry2yiY7cGF2agjIp7nGZbTnsuaISM_KI3HIjN-bJX9HxfzoM7WS7JVz0zQ-R8-7m6HyClj00hGJetHYjUyF8DqqtsCy6k4J8rHphPJxnEPKhm5-9hoyxo8042AheQIhhen2Fx7dOUfY5vzsrXE8t-CefDdZbGqpGqQs0YBOMFFs2JYw37uAGkZdoTOEpolld64BBg5L_qPfTf3gn7Zyi_qOoK5zpV__m3KG2QPI9Pobxrlr76WqrPMsBfI4CormpxOAWo2WrVjLxomZfyv8s1vD_H_-6JjzAZ0eLrhcUhJc="

# Yeni event loop oluştur
loop = asyncio.new_event_loop()

# Telegram Client tanımla (loop bu loop)
client = TelegramClient(StringSession(string_session), api_id, api_hash, loop=loop)

# Thread içinde client başlat
def basla():
    asyncio.set_event_loop(loop)  # ← bunu eklemek şart!
    try:
        loop.run_until_complete(client.start())
        print("✅ Telegram Client başlatıldı.")
        loop.run_forever()
    except Exception as e:
        print("❌ Telegram başlatılırken hata:", str(e))

# Thread başlat
threading.Thread(target=basla, daemon=True).start()

# Komut gönderme fonksiyonu
async def gonder_ve_bekle(komut):
    print("🔁 Komut gönderiliyor:", komut)
    cevaplar = []
    cevap_event = asyncio.Event()

    @client.on(events.NewMessage(chats='LightSorgupanelibot'))
    async def handler(event):
        print("📩 Cevap geldi:", event.text[:100])
        cevaplar.append(event.text)
        cevap_event.set()

    try:
        await client.send_message('LightSorgupanelibot', komut)
        await asyncio.wait_for(cevap_event.wait(), timeout=20)
    except Exception as e:
        client.remove_event_handler(handler)
        print("❌ HATA:", str(e))
        return f"⛔ Hata oluştu: {str(e)}"

    await asyncio.sleep(2)
    client.remove_event_handler(handler)
    return "\n---\n".join(cevaplar)
