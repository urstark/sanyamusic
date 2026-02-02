import asyncio
from pyrogram import filters
from SANYAMUSIC import app
from SANYAMUSIC.utils.admin_check import is_admin
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

# Database setup
mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC
edit_db = db.edit_defender
whitelist_db = db.defender_whitelist

async def is_edit_defender_on(chat_id):
    data = await edit_db.find_one({"chat_id": chat_id})
    return data and data.get("status") == "on"

async def is_whitelisted(chat_id, user_id):
    data = await whitelist_db.find_one({"chat_id": chat_id})
    return data and user_id in data.get("users", [])

@app.on_message(filters.command("editdefender") & filters.group)
async def edit_defender_toggle(client, message):
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    if len(message.command) < 2:
        is_on = await is_edit_defender_on(message.chat.id)
        status_text = "ᴇɴᴀʙʟᴇᴅ" if is_on else "ᴅɪsᴀʙʟᴇᴅ"
        return await message.reply(f"❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {status_text}.**\n\n<b>ᴜsᴀɢᴇ:</b> /editdefender [on/off]")
    
    state = message.command[1].lower()
    if state == "on":
        await edit_db.update_one({"chat_id": message.chat.id}, {"$set": {"status": "on"}}, upsert=True)
        await message.reply("❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ᴇɴᴀʙʟᴇᴅ.**\n\nɪ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛʜᴀᴛ ɢᴇᴛs ᴇᴅɪᴛᴇᴅ ʙʏ ɴᴏɴ-ᴀᴅᴍɪɴs.")
    elif state == "off":
        await edit_db.update_one({"chat_id": message.chat.id}, {"$set": {"status": "off"}}, upsert=True)
        await message.reply("❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ᴅɪsᴀʙʟᴇᴅ.**")
    else:
        await message.reply("<b>ᴜsᴀɢᴇ:</b> /editdefender [on/off]")

async def delete_edited_msg_task(message):
    try:
        await message.delete()
        user_mention = message.from_user.mention if message.from_user else "Unknown"
        warn_msg = await message.reply(
            f"❍ {user_mention}, **ᴇᴅɪᴛɪɴɢ ᴍᴇssᴀɢᴇs ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ.**\n"
            "ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ."
        )
        # Delete the warning after 5 seconds to keep chat clean
        await asyncio.sleep(5)
        await warn_msg.delete()
    except Exception:
        pass

@app.on_edited_message(filters.group & ~filters.me)
async def edit_watcher(client, message):
    # Check if feature is enabled
    if not await is_edit_defender_on(message.chat.id):
        return

    # Ignore if user is whitelisted
    user_id = message.from_user.id if message.from_user else 0
    if user_id and await is_whitelisted(message.chat.id, user_id):
        return

    # Use create_task to avoid blocking the bot
    asyncio.create_task(delete_edited_msg_task(message))

__module__ = "Eᴅɪᴛ Dᴇғᴇɴᴅᴇʀ"
__help__ = """
**❍ ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ**

ᴛʜɪs ᴍᴏᴅᴜʟᴇ ʜᴇʟᴘs ᴛᴏ ᴋᴇᴇᴘ ᴛʜᴇ ᴄʜᴀᴛ ᴄʟᴇᴀɴ ʙʏ ᴅᴇʟᴇᴛɪɴɢ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs ғʀᴏᴍ ɴᴏɴ-ᴀᴅᴍɪɴ ᴜsᴇʀs.

**ᴄᴏᴍᴍᴀɴᴅs:**
» /editdefender [on/off] : ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ.
"""
