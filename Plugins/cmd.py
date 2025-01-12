import asyncio
import pytz
from config import ADMINS
from pyrogram import Client, filters
from bot import Bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from helper_func import *
from Script import script
from database.database import *

@Bot.on_message(filters.command("verify"))
async def confirm_command_handler(client, message: Message):
    user_id = message.from_user.id

    # Set user state to 'processing_payment'
    set_state(user_id, "processing_payment")

    # Send a message prompting for the UTR
    prompt_message = await message.reply_text(
        "📝 **Please enter your 12-digit UTR number to verify your payment.**"
    )

    try:
        # Wait for the user to input their UTR or timeout after 150 seconds
        await asyncio.sleep(150)

        if get_state(user_id) == "processing_payment":
            reset_state(user_id)

            # Update the prompt message if the UTR was not provided
            await prompt_message.edit_text(
                "⏳ **Time's up!** You did not send a UTR number in time. Please try again. 😮‍💨",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Try Again ♻️", callback_data="retry_confirm")
                ]])
            )
    except Exception as e:
        print(f"Error during timeout handling: {e}")


@Bot.on_callback_query(filters.regex(r"^retry_confirm$"))
async def retry_confirm_handler(client, query):
    user_id = query.from_user.id

    # Reset the state in case it's still set
    reset_state(user_id)

    # Prompt the user to input the UTR again
    set_state(user_id, "processing_payment")
    prompt_message = await query.message.edit_text(
        "📝 **Please enter your 12-digit UTR number to verify your payment.**"
    )

    try:
        # Wait for the user to input their UTR or timeout after 150 seconds
        await asyncio.sleep(150)

        if get_state(user_id) == "processing_payment":
            reset_state(user_id)

            # Update the prompt message if the UTR was not provided
            await prompt_message.edit_text(
                "⏳ **Time's up!** You did not send a UTR number in time. Please try again. 😮‍💨",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Try Again ♻️", callback_data="retry_confirm")
                ]])
            )
    except Exception as e:
        print(f"Error during timeout handling: {e}")

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

@Bot.on_message(filters.command("removep") & filters.user(ADMINS))
async def remove_premium_cmd_handler(client: Client, message):
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])

            # Retrieve user data to confirm existence
            user_data, user_data2, user_data3 = await db.get_user(user_id)

            if any([user_data, user_data2, user_data3]):  # If user exists in any database
                # Remove premium access from all databases
                result1 = await db.col.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
                result2 = await db.col2.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
                result3 = await db.col3.update_one({"id": user_id}, {"$set": {"expiry_time": None}})

                # Check if any database was updated
                if result1.modified_count > 0 or result2.modified_count > 0 or result3.modified_count > 0:
                    user = await client.get_users(user_id)
                    user_mention = user.mention
                    await message.reply_text(
                        f"✅ Premium access removed for {user_mention} (`{user_id}`) across all databases."
                    )
                else:
                    await message.reply_text(
                        f"⚠️ No changes made. Premium access might already be removed for user `{user_id}`."
                    )
            else:
                await message.reply_text(f"⚠️ User with ID `{user_id}` not found in any database.")
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid integer user ID.")
        except Exception as e:
            await message.reply_text(f"❌ Error occurred: {e}")
    else:
        await message.reply_text("**Usage: /removep user_id**")

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