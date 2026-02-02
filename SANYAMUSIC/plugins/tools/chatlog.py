import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER_ID as LOG_GROUP_ID
from SANYAMUSIC import app 
from pyrogram.errors import RPCError, ChatAdminRequired # Added ChatAdminRequired
from typing import Union, Optional
from PIL import Image, ImageDraw, ImageFont
import asyncio, os, aiohttp
from pathlib import Path
from pyrogram.enums import ParseMode

photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(client, message):    
    chat = message.chat
    
    # Attempt to get an invite link safely
    try:
        link = await client.export_chat_invite_link(chat.id)
    except ChatAdminRequired:
        # Fallback if bot is not admin or lacks "Invite Users via Link" permission
        link = f"https://t.me/{chat.username}" if chat.username else "Private Group (No Link Permission)"
    except Exception:
        link = "Link Unavailable"

    for member in message.new_chat_members:
        if member.id == client.me.id:
            count = await client.get_chat_members_count(chat.id)
            username_text = f"@{chat.username}" if chat.username else "Private Chat"
            
            msg = (
                f"📝 ᴍᴜsɪᴄ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ\n\n"
                f"____________________________________\n\n"
                f"📌 ᴄʜᴀᴛ ɴᴀᴍᴇ: {chat.title}\n"
                f"🍂 ᴄʜᴀᴛ ɪᴅ: {chat.id}\n"
                f"🔐 ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ: {username_text}\n"
                f"🛰 ᴄʜᴀᴛ ʟɪɴᴋ: [ᴄʟɪᴄᴋ]({link})\n"
                f"📈 ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs: {count}\n"
                f"🤔 ᴀᴅᴅᴇᴅ ʙʏ: {message.from_user.mention if message.from_user else 'Unknown'}"
            )
            
            # Prepare button only if a valid link exists
            buttons = []
            if link.startswith("http"):
                buttons.append([InlineKeyboardButton("sᴇᴇ ɢʀᴏᴜᴘ👀", url=link)])
                
            await client.send_photo(
                LOG_GROUP_ID, 
                photo=random.choice(photo), 
                caption=msg, 
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
            )

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client, message: Message):
    if (await client.get_me()).id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        chat_id = message.chat.id
        left = f"✫ <b><u>#𝐋ᴇғᴛ_𝐆ʀᴏᴜᴘ</u></b> ✫\n\n𝐂ʜᴀᴛ 𝐓ɪᴛʟᴇ : {title}\n\n𝐂ʜᴀᴛ 𝐈ᴅ : {chat_id}\n\n𝐑ᴇᴍᴏᴠᴇᴅ 𝐁ʏ : {remove_by}\n\n𝐁ᴏᴛ : @{client.me.username}"
        await client.send_photo(LOG_GROUP_ID, photo=random.choice(photo), caption=left)
