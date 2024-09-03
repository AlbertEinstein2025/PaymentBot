from config import ADMINS
from pyrogram import Client, filters
from bot import Bot
from helper_func import give_premium
import pytz


@Bot.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def addpremium_cmd_handler(client: Client, message):
    if len(message.command) == 3:
        user_id = int(message.command[1])
        time_input = message.command[2]

        current_time, new_expiry_time = await give_premium(user_id, time_input)

        if new_expiry_time:  # Check if premium was added successfully
            ist = pytz.timezone('Asia/Kolkata')
            current_time_ist = current_time.astimezone(ist)
            new_expiry_time_ist = new_expiry_time.astimezone(ist)

            user = await client.get_users(user_id)
            user_mention = user.mention

            await message.reply_text(
                f"**Premium added successfully ✅**\n\n"
                f"👤 User: {user_mention}\n"
                f"🎭 User ID: {user_id}\n"
                f"⏰ Premium Access: {time_input}\n\n"
                f"⏳ Joining Date: {current_time_ist.strftime('%d-%m-%Y')}\n"
                f"⏱️ Joining Time: {current_time_ist.strftime('%I:%M:%S %p')}\n\n"
                f"⌛️ New Expiry Date: {new_expiry_time_ist.strftime('%d-%m-%Y')}\n"
                f"⏱️ New Expiry Time: {new_expiry_time_ist.strftime('%I:%M:%S %p')}\n"
            )
        else:
            await message.reply_text("**Invalid time format. Please use '1day', '1hour', '1min', '1month', or '1year'**")
    else:
        await message.reply_text("**Usage: /addpremium user_id time**")
