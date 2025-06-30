import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 7637015444
api_hash = '18c5be05094b146ef29b0cb6f6601f1f'
string_session = "1ApWapzMBuxkq-wNsXTFVUnrBE2PYUbLujSuXjDUgV09wd8cDS8PUfkJgyBs_gcF0Wx_XbjbMKUEiXbSHdo-QyVY4sCjQjYlUXRSkup4uHC834L8VJcm1aYnny9kFwRMPDldKbvK9zxUVvmIgfDy3ZZcKz0oeXuAlLABwORG-ZBk_mLuokrTkg7OIIMVF9StytoFeFbvNVcI9OrWAPv2UCuy888JnR6OsAMPFfbNnQ7Dcqmv2sQjc0YaddRxnQoObwsT6Rv8Ubz1tz6KocpUlTTpYvb-YydybHmEGOEndwrJL8qB2Ky5xEvcTG65QQI0JNXan1m9xps2O2oEMXNRaSINdHy3KuPM="

client = TelegramClient(StringSession(string_session), api_id, api_hash)

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

    await asyncio.sleep(30)
    client.remove_event_handler(handler)
    return "\n---\n".join(cevaplar)

# Jandarma
async def gonder_jandarma_ihbar(konum, detay):
    return await gonder_ihbarli('KenevizihbarBot', '/jandarmaihbar', konum, detay)

# EGM
async def gonder_egm_ihbar(konum, detay):
    return await gonder_ihbarli('KenevizihbarBot', '/egmihbar', konum, detay)

# USOM
async def gonder_usom_ihbar(konum, detay):
    return await gonder_ihbarli('KenevizihbarBot', '/usomihbar', konum, detay)

# Ortak Fonksiyon
async def gonder_ihbarli(bot_adi, komut, konum, detay):
    cevaplar = []
    cevap_event = asyncio.Event()

    @client.on(events.NewMessage(chats=bot_adi))
    async def handler(event):
        cevaplar.append(event.text)
        cevap_event.set()

    await client.send_message(bot_adi, komut)
    await asyncio.wait_for(cevap_event.wait(), timeout=10)
    cevap_event.clear()

    await asyncio.sleep(1)
    await client.send_message(bot_adi, konum)
    await asyncio.wait_for(cevap_event.wait(), timeout=10)
    cevap_event.clear()

    await asyncio.sleep(1)
    await client.send_message(bot_adi, detay)
    await asyncio.sleep(3)

    client.remove_event_handler(handler)
    return "\n---\n".join(cevaplar)

async def baslat():
    await client.start()
    print("✅ Telegram client başlatıldı.")

if __name__ == "__main__":
    asyncio.run(baslat())
