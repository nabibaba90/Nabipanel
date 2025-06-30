import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask, request, jsonify
import threading

api_id = 24396967
api_hash = '7ddf52c9da17c98550cb937552ebffb8'
string_session = "1ApWapzMBuzs9njNDBHSqIOUiOdyn1y94Q3V-83VeoMC_uWXUo1K_ry2yiY7cGF2agjIp7nGZbTnsuaISM_KI3HIjN-bJX9HxfzoM7WS7JVz0zQ-R8-7m6HyClj00hGJetHYjUyF8DqqtsCy6k4J8rHphPJxnEPKhm5-9hoyxo8042AheQIhhen2Fx7dOUfY5vzsrXE8t-CefDdZbGqpGqQs0YBOMFFs2JYw37uAGkZdoTOEpolld64BBg5L_qPfTf3gn7Zyi_qOoK5zpV__m3KG2QPI9Pobxrlr76WqrPMsBfI4CormpxOAWo2WrVjLxomZfyv8s1vD_H_-6JjzAZ0eLrhcUhJc="

client = TelegramClient(StringSession(string_session), api_id, api_hash)
app = Flask(__name__)

async def gonder_ve_bekle(komut):
    cevaplar = []
    cevap_event = asyncio.Event()

    @client.on(events.NewMessage(chats='LightSorgupanelibot'))
    async def handler(event):
        cevaplar.append(event.text)
        cevap_event.set()

    await client.send_message('LightSorgupanelibot', komut)

    try:
        await asyncio.wait_for(cevap_event.wait(), timeout=15)
    except asyncio.TimeoutError:
        client.remove_event_handler(handler)
        return "Cevap gelmedi."

    client.remove_event_handler(handler)
    return "\n---\n".join(cevaplar)

# Burada diğer ihbar fonksiyonlarını da ekle (senin verdiğin şekilde)

async def baslat():
    await client.start()
    print("✅ Telegram client başlatıldı.")

# Flask ile panelden sorgu alma endpoint'i:
@app.route('/sorgu', methods=['POST'])
def sorgu_al():
    data = request.json
    if not data or 'komut' not in data:
        return jsonify({'error': 'Komut gönderilmedi.'}), 400
    komut = data['komut']

    # Async fonksiyon çağrısını senkrona çevirelim
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        cevap = loop.run_until_complete(gonder_ve_bekle(komut))
    finally:
        loop.close()

    return jsonify({'cevap': cevap})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Telegram client başlat
    loop.run_until_complete(baslat())

    # Flask serveri ayrı threadde başlat
    t = threading.Thread(target=run_flask)
    t.start()

    # Telegram client event loop devam etsin
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Program durduruldu.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
