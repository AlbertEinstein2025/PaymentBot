from config import ADMINS
from pyrogram import Client, filters
from bot import Bot
from pyrogram.types import Message
from helper_func import give_premium, set_state
from Script import script
import pytz
from database.database import *

@Bot.on_message(filters.command("confirm"))
async def confirm_command_handler(client, message: Message):
    """
    Command to initiate the UTR verification process.
    Redirects to handle_utr_input after asking for the UTR.
    """
    user_id = message.from_user.id

    # Set user state to 'processing_payment'
    set_state(user_id, "processing_payment")

    # Prompt user to input their UTR
    await message.reply_text(
        "📝 **Please enter your 12-digit UTR number to verify your payment.**"
    )

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
                script.PREMIUM_ADDED.format(
                    user_mention,
                    user_id,
                    time_input,
                    current_time_ist.strftime('%d-%m-%Y'),
                    current_time_ist.strftime('%I:%M:%S %p'),
                    new_expiry_time_ist.strftime('%d-%m-%Y'),
                    new_expiry_time_ist.strftime('%I:%M:%S %p')
                )
            )
        else:
            await message.reply_text("**Invalid time format. Please use '1day', '1hour', '1min', '1month', or '1year'**")
    else:
        await message.reply_text("**Usage: /addpremium user_id time**")

@Bot.on_message(filters.command("removeutr") & filters.user(ADMINS))
async def handle_remove_utr_command(client, message):
    """
    Handles the /removeutr <utr> command to remove a UTR from the database.
    Only accessible to users listed in ADMINS.
    """
    try:
        # Extract the UTR number from the message
        command_parts = message.text.strip().split(maxsplit=1)
        if len(command_parts) != 2:
            await message.reply("⚠️ **Usage:** /removeutr <UTR>")
            return
        
        utr = command_parts[1].strip()
        
        if not utr:
            await message.reply("⚠️ **Error:** UTR cannot be empty. Please provide a valid UTR.")
            return
        
        # Call the function to remove the UTR
        success = await remove_used_utr(utr)
        
        # Send appropriate response
        if success:
            await message.reply(f"✅ **UTR** `{utr}` has been successfully removed from the database.")
        else:
            await message.reply(f"⚠️ **UTR** `{utr}` not found in the database.")
    except Exception as e:
        # Log the exception (if you have a logging system in place)
        print(f"Error in /removeutr command: {e}")
        await message.reply(f"❌ **An error occurred:** {e}")