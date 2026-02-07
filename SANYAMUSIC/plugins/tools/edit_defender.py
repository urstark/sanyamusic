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
    # Only admins can change the settings of the bot
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    if len(message.command) < 2:
        is_on = await is_edit_defender_on(message.chat.id)
        status_text = "ᴇɴᴀʙʟᴇᴅ" if is_on else "ᴅɪsᴀʙʟᴇᴅ"
        return await message.reply(f"❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {status_text}.**\n\n<b>ᴜsᴀɢᴇ:</b> /editdefender [on/off]")
    
    state = message.command[1].lower()
    if state == "on":
        await edit_db.update_one({"chat_id": message.chat.id}, {"$set": {"status": "on"}}, upsert=True)
        await message.reply("❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ᴇɴᴀʙʟᴇᴅ.**\n\nɪ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs. ᴏɴʟʏ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs ᴄᴀɴ ʙʏᴘᴀss ᴛʜɪs.")
    elif state == "off":
        await edit_db.update_one({"chat_id": message.chat.id}, {"$set": {"status": "off"}}, upsert=True)
        await message.reply("❍ **ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ᴅɪsᴀʙʟᴇᴅ.**")
    else:
        await message.reply("<b>ᴜsᴀɢᴇ:</b> /editdefender [on/off]")

async def delete_edited_msg_task(message):
    try:
        await message.delete()
        user_mention = message.from_user.mention if message.from_user else "Unknown User"
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
    # 1. FIX: Ensure it only triggers on actual edits, not new message glitches
    if not message.edit_date:
        return

    # 2. Check if feature is enabled for the group
    if not await is_edit_defender_on(message.chat.id):
        return

    # 3. Whitelist Bypass: Works for both admins and normal users
    user_id = message.from_user.id if message.from_user else 0
    if user_id and await is_whitelisted(message.chat.id, user_id):
        return

    # 4. Action: Delete edited messages for everyone else (including non-whitelisted admins)
    asyncio.create_task(delete_edited_msg_task(message))

__module__ = "Eᴅɪᴛ Dᴇғᴇɴᴅᴇʀ"
__help__ = """
**❍ ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ**

ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴅᴇʟᴇᴛᴇs ᴍᴇssᴀɢᴇs ᴛʜᴀᴛ ɢᴇᴛ ᴇᴅɪᴛᴇᴅ ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴄʜᴀᴛ ᴍᴀɴɪᴘᴜʟᴀᴛɪᴏɴ.

**ᴄᴏᴍᴍᴀɴᴅs:**
» /editdefender [on/off] : ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ.

**ɴᴏᴛᴇ:**
ᴏɴʟʏ **ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs** ᴄᴀɴ ʙʏᴘᴀss ᴛʜɪs. ɴᴏɴ-ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴀᴅᴍɪɴs ᴡɪʟʟ sᴛɪʟʟ ʜᴀᴠᴇ ᴛʜᴇɪʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs ᴅᴇʟᴇᴛᴇᴅ.
"""
