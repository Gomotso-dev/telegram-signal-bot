import os
from telethon import TelegramClient

client = TelegramClient("telegram_listener", int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])

async def main():
    async for d in client.iter_dialogs():
        if d.is_channel or d.is_group:
            kind = "channel" if d.is_channel and not d.is_group else "group"
            print(f"{d.id} | {kind} | {d.name}")

with client:
    client.loop.run_until_complete(main())
    
    
