import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 17570480
api_hash = '18c5be05094b146ef29b0cb6f6601f1f'
string_session = "1ApWapzMBuxCTW8RXyL9M47P-wh6RvxQ1gLJ8fLCZWBvRxd4G9T7-H3kDyvWOPMbcD6BIci1RkDJEWYQxV8GVdpTUK2LmiogGyf8SnFSkfGpZIVM3pzlaMAcyYmiCe1DZKm4AhxQrnwIq-LJt-lfc2FUY3vl9vA8Sd1OsB1n6f1aZ6Oe-4pST5mzm0h5hXi6E8xVyzHls4WAY7gA1tAaWJHz98CNA7TlwB5VbZQ0Y6IysrxMH-L2TrZzmBvjoo2fGhds7hsqq7kSVZp2aS33cJUGlekj3yhzukq1WO1-HC1NoqCp__1SxUgv3O9E5CuQxUWOSv3h-ff0i2DLkU7kW_aG0HU2jm-A="

client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def gonder_ve_bekle(bot_adi, komut):
    cevaplar = []
    cevap_event = asyncio.Event()

    @client.on(events.NewMessage(chats=bot_adi))
    async def handler(event):
        cevaplar.append(event.text)
        cevap_event.set()

    await client.send_message(bot_adi, komut)
    print(f"[{bot_adi}] Komut gönderildi: {komut}")

    try:
        await asyncio.wait_for(cevap_event.wait(), timeout=15)
    except asyncio.TimeoutError:
        client.remove_event_handler(handler)
        return "⛔ Cevap gelmedi."

    await asyncio.sleep(5)
    client.remove_event_handler(handler)
    return "\n---\n".join(cevaplar)

async def main():
    await client.start()
    print("✅ Telegram client başlatıldı.\n")

    # Sorgu botu (/adsoyad)
    cevap1 = await gonder_ve_bekle("LightSorgupanelibot", "/adsoyad Ahmet Kaya Ankara Keçiören")
    print("🟢 /adsoyad cevabı:\n", cevap1)

    # Keneviz botu (/jandarmaihbar)
    cevap2 = await gonder_ve_bekle("KenevizihbarBot", "/jandarmaihbar")
    print("🟢 /jandarmaihbar cevabı:\n", cevap2)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
