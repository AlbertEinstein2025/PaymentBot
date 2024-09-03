import logging
import asyncio
import sys
import os
import subprocess  # Import for running shell commands
from pyrogram import filters
from bot import Bot
from config import ADMINS

@Bot.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(bot, message):
    try:
        # Informing the user that the bot is restarting and pulling the latest changes
        msg = await message.reply_text("<b><blockquote>Pulling the latest updates and restarting the bot...</blockquote></b>")
        
        # Pull the latest code from the upstream repository
        git_pull = subprocess.run(["git", "pull"], capture_output=True, text=True)
        
        # Log the output of the git pull command
        if git_pull.returncode == 0:
            await msg.edit(f"<b><blockquote>Updates pulled successfully:\n\n{git_pull.stdout}</blockquote></b>")
        else:
            await msg.edit(f"<b><blockquote>Failed to pull updates:\n\n{git_pull.stderr}</blockquote></b>")
            return  # If git pull fails, do not restart the bot
        
        await asyncio.sleep(3)

        # Ensure the message edit is done before restarting
        await msg.edit("<b><blockquote>✅️ Bot is restarted! Now fuck me!!!</blockquote></b>")

    except Exception as e:
        print(f"Error editing message: {e}")  # Print the error for debugging
        pass  # Ignore errors in case the message is deleted

    finally:
        # Restart the bot after the message has been edited (or the attempt has failed)
        os.execl(sys.executable, sys.executable, *sys.argv)
