import asyncio
from pyrogram import filters
from SANYAMUSIC import app
from SANYAMUSIC.utils.admin_check import is_admin
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

# Database setup
mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC
media_db = db.media_defender
whitelist_db = db.defender_whitelist

# Default time: 1 hour (3600 seconds)
DEFAULT_TIME = 3600

async def get_media_config(chat_id):
    data = await media_db.find_one({"chat_id": chat_id})
    if not data:
        return False, DEFAULT_TIME
    return data.get("status") == "on", data.get("time", DEFAULT_TIME)

async def is_whitelisted(chat_id, user_id):
    data = await whitelist_db.find_one({"chat_id": chat_id})
    return data and user_id in data.get("users", [])

def parse_time(time_str):
    if time_str.endswith("s"): return int(time_str[:-1])
    if time_str.endswith("m"): return int(time_str[:-1]) * 60
    if time_str.endswith("h"): return int(time_str[:-1]) * 3600
    if time_str.endswith("d"): return int(time_str[:-1]) * 86400
    return int(time_str)

@app.on_message(filters.command(["mediadefender", "automedia"]) & filters.group)
async def media_defender_toggle(client, message):
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    if len(message.command) < 2:
        is_on, time_val = await get_media_config(message.chat.id)
        status_text = "ᴇɴᴀʙʟᴇᴅ" if is_on else "ᴅɪsᴀʙʟᴇᴅ"
        return await message.reply(
            f"❍ **ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {status_text}.**\n"
            f"**ᴛɪᴍᴇ:** {time_val}s\n\n"
            "<b>ᴜsᴀɢᴇ:</b> /mediadefender [on/off] [time]\n\n"
            "<b>ᴇxᴀᴍᴘʟᴇs:</b>\n"
            "/mediadefender on 30m (ᴅᴇʟᴇᴛᴇ ᴍᴇᴅɪᴀ ᴀғᴛᴇʀ 30 ᴍɪɴs)\n"
            "/mediadefender on 1h (ᴅᴇʟᴇᴛᴇ ᴍᴇᴅɪᴀ ᴀғᴛᴇʀ 1 ʜᴏᴜʀ)\n"
            "/mediadefender off"
        )
    
    state = message.command[1].lower()
    
    if state == "on":
        time_val = DEFAULT_TIME
        if len(message.command) > 2:
            try:
                time_val = parse_time(message.command[2])
            except ValueError:
                return await message.reply("❍ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ. ᴜsᴇ s/ᴍ/ʜ/ᴅ (ᴇ.ɢ., 60s, 10m, 1h).")
        
        await media_db.update_one(
            {"chat_id": message.chat.id}, 
            {"$set": {"status": "on", "time": time_val}}, 
            upsert=True
        )
        await message.reply(f"❍ **ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ ᴇɴᴀʙʟᴇᴅ.**\n\nᴀʟʟ ᴍᴇᴅɪᴀ sᴇɴᴛ ʙʏ ɴᴏɴ-ᴀᴅᴍɪɴs ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ **{message.command[2] if len(message.command) > 2 else '1h'}**.")
        
    elif state == "off":
        await media_db.update_one({"chat_id": message.chat.id}, {"$set": {"status": "off"}}, upsert=True)
        await message.reply("❍ **ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ ᴅɪsᴀʙʟᴇᴅ.**")
    else:
        await message.reply("<b>ᴜsᴀɢᴇ:</b> /mediadefender [on/off] [time]")

async def delete_media_task(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

@app.on_message(filters.group & (filters.photo | filters.video | filters.document | filters.audio | filters.voice | filters.sticker | filters.animation) & ~filters.me)
async def media_watcher(client, message):
    is_on, delay = await get_media_config(message.chat.id)
    if not is_on:
        return

    # Ignore if user is whitelisted
    user_id = message.from_user.id if message.from_user else 0
    if user_id and await is_whitelisted(message.chat.id, user_id):
        return

    # Wait for the specified time
    asyncio.create_task(delete_media_task(message, delay))

__module__ = "Mᴇᴅɪᴀ Dᴇғᴇɴᴅᴇʀ"
__help__ = """
**❍ ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ**

ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇs ᴍᴇᴅɪᴀ ᴍᴇssᴀɢᴇs sᴇɴᴛ ʙʏ ɴᴏɴ-ᴀᴅᴍɪɴ ᴜsᴇʀs ᴀғᴛᴇʀ ᴀ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ.

**ᴄᴏᴍᴍᴀɴᴅs:**
» /mediadefender [on/off] [time] : ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ.
  ᴇxᴀᴍᴘʟᴇ: `/mediadefender on 10m` (ᴅᴇʟᴇᴛᴇs ᴍᴇᴅɪᴀ ᴀғᴛᴇʀ 10 ᴍɪɴᴜᴛᴇs)
  ᴀʟɪᴀsᴇs: `/automedia`
"""
