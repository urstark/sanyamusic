
import asyncio
from pyrogram import filters
from pyrogram import Client
from SANYAMUSIC import app
from SANYAMUSIC.misc import SUDOERS


@app.on_message(filters.command("raid", prefixes=".") & SUDOERS)
async def spam_command(client, message):
    # Default values
    count = 5
    text = "ғᴜᴍᴄᴋ ᴜ!"
    
    try:
        await message.delete()
    except Exception as e:
        print(f"Eʀʀᴏʀ ᴅᴇʟᴇᴛɪɴɢ ʀᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ: {e}")

    if not message.reply_to_message:
        await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴀɪᴅ ᴛʜᴇᴍ.")
        return

    # Parsing arguments
    command_args = message.text.split(maxsplit=1)
    if len(command_args) > 1:
        args = command_args[1].split(maxsplit=1)
        try:
            count = int(args[0])
            if len(args) > 1:
                text = args[1]
        except ValueError:
            text = command_args[1] # If first arg is not a number, it's the text
        except IndexError:
            pass # Use default text

    user_to_raid = message.reply_to_message.from_user.mention

    for _ in range(count):
        await message.reply_to_message.reply_text(f"{user_to_raid} {text}")
        await asyncio.sleep(0.2)
