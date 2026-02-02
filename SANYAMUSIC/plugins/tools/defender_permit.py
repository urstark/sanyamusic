from pyrogram import filters
from SANYAMUSIC import app
from SANYAMUSIC.utils.admin_check import is_admin
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC
whitelist_db = db.defender_whitelist

async def add_permit(chat_id, user_id):
    await whitelist_db.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )

async def remove_permit(chat_id, user_id):
    await whitelist_db.update_one(
        {"chat_id": chat_id},
        {"$pull": {"users": user_id}},
        upsert=True
    )

async def get_permitted_users(chat_id):
    data = await whitelist_db.find_one({"chat_id": chat_id})
    return data.get("users", []) if data else []

@app.on_message(filters.command("permit") & filters.group)
async def permit_user(client, message):
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    user = None
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            return await message.reply("❍ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
    else:
        return await message.reply("<b>ᴜsᴀɢᴇ:</b> /permit [reply/username/userid]")

    if not user:
        return await message.reply("❍ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")

    await add_permit(message.chat.id, user.id)
    await message.reply(f"❍ {user.mention} ʜᴀs ʙᴇᴇɴ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ғʀᴏᴍ ᴇᴅɪᴛ ᴀɴᴅ ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ.")

@app.on_message(filters.command("unpermit") & filters.group)
async def unpermit_user(client, message):
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    user = None
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            return await message.reply("❍ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
    else:
        return await message.reply("<b>ᴜsᴀɢᴇ:</b> /unpermit [reply/username/userid]")

    if not user:
        return await message.reply("❍ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")

    await remove_permit(message.chat.id, user.id)
    await message.reply(f"❍ {user.mention} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴡʜɪᴛᴇʟɪsᴛ.")

@app.on_message(filters.command(["permitted", "whitelist", "allowlist"]) & filters.group)
async def list_permitted(client, message):
    if not await is_admin(message):
        return await message.reply("» **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    
    users = await get_permitted_users(message.chat.id)
    if not users:
        return await message.reply("❍ **ɴᴏ ᴜsᴇʀs ᴀʀᴇ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    
    text = "**❍ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs:**\n"
    for user_id in users:
        try:
            user = await client.get_users(user_id)
            text += f"➻ {user.mention}\n"
        except:
            text += f"➻ {user_id}\n"
    
    await message.reply(text)

__module__ = "Dᴇғᴇɴᴅᴇʀ Pᴇʀᴍɪᴛ"
__help__ = """
**❍ ᴅᴇғᴇɴᴅᴇʀ ᴡʜɪᴛᴇʟɪsᴛ**

ᴍᴀɴᴀɢᴇ ᴜsᴇʀs ᴡʜᴏ ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ʙʏᴘᴀss ᴇᴅɪᴛ ᴅᴇғᴇɴᴅᴇʀ ᴀɴᴅ ᴍᴇᴅɪᴀ ᴅᴇғᴇɴᴅᴇʀ.

**ᴄᴏᴍᴍᴀɴᴅs:**
» /permit [reply/username/userid] : ᴡʜɪᴛᴇʟɪsᴛ ᴀ ᴜsᴇʀ.
» /unpermit [reply/username/userid] : ʀᴇᴍᴏᴠᴇ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ᴡʜɪᴛᴇʟɪsᴛ.
» /permitted : ᴠɪᴇᴡ ᴛʜᴇ ʟɪsᴛ ᴏғ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs.
  ᴀʟɪᴀsᴇs: `/whitelist`, `/allowlist`
"""
