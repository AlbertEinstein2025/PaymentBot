from config import *
from pyrogram import Client 
from datetime import datetime
from aiohttp import web

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            bot_token=BOT_TOKEN,
            api_id=API_ID,
            api_hash=API_HASH,
            sleep_threshold=5,
            workers=100,
            plugins={'root': 'Plugins'}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        self.uptime = datetime.now()
        print(f"New session started for {me.first_name}({me.username})")

    async def stop(self):
        await super().stop()
        print("Session stopped. Bye!!")
