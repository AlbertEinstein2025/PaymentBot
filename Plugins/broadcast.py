import asyncio
from pyrogram import filters, __version__
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS
from database.database import del_user, full_userbase

WAIT_MSG = "Please Wait"
REPLY_ERROR = "Error"

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & (filters.command('broadcast') | filters.command('pbroadcast')) & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    user_id = message.from_user.id
    if message.reply_to_message:
        query = await full_userbase()
        total_users = len(query)
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pin_message = message.command[0] == 'pbroadcast'
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        
        for chat_id in query:
            try:
                sent_message = await broadcast_msg.copy(chat_id)  # Store the sent message
                successful += 1
                
                if pin_message:  # Pin the message only if /pbroadcast was used
                    try:
                        await client.pin_chat_message(chat_id, sent_message.id, both_sides=True)
                    except errors.ChatAdminRequired:
                        print(f"Bot is not an admin in chat {chat_id}, cannot pin message.")
                    except Exception as e:
                        print(f"Error pinning message in chat {chat_id}: {e}")

            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_message = await broadcast_msg.copy(chat_id)  # Store the sent message
                successful += 1
                
                if pin_message:  # Pin the message only if /pbroadcast was used
                    try:
                        await client.pin_chat_message(chat_id, sent_message.id, both_sides=True)
                    except errors.ChatAdminRequired:
                        print(f"Bot is not an admin in chat {chat_id}, cannot pin message.")
                    except Exception as e:
                        print(f"Error pinning message in chat {chat_id}: {e}")
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
            if total % 2 == 0 or total == total_users:
                users_left = total_users - total
                progress_message = f"""
<b><u>Broadcast in Progress</u>
<blockquote>
> Total Users: <code>{total_users}</code>
> Completed: <code>{total}</code>
> Users Left: <code>{users_left}</code>
> Successful: <code>{successful}</code>
> Blocked Users: <code>{blocked}</code>
> Deleted Accounts: <code>{deleted}</code>
> Unsuccessful: <code>{unsuccessful}</code>   
</blockquote>
            """
                await pls_wait.edit(progress_message)

        status = f"""<b><u>Broadcast Completed</u>

<blockquote>Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></blockquote></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
