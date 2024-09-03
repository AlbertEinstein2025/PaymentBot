from config import *
from pyrogram import Client 
from datetime import datetime

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            bot_token=BOT_TOKEN,
            api_id=API_ID,
            api_hash=API_HASH,
            workers=20,
            plugins={'root': 'Plugins'}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now()
        print(f"New session started for {me.first_name}({me.username})")
        print(f""" \n      

███╗░░██╗██╗███╗░░██╗░░░░░██╗░█████╗░██╗░░██╗
████╗░██║██║████╗░██║░░░░░██║██╔══██╗╚██╗██╔╝
██╔██╗██║██║██╔██╗██║░░░░░██║███████║░╚███╔╝░
██║╚████║██║██║╚████║██╗░░██║██╔══██║░██╔██╗░
██║░╚███║██║██║░╚███║╚█████╔╝██║░░██║██╔╝╚██╗
╚═╝░░╚══╝╚═╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝
                                            \n""")

    async def stop(self):
        await super().stop()
        print("Session stopped. Bye!!")
