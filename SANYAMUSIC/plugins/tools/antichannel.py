from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ChatMemberStatus

from config import COMMAND_PREFIXES, MONGO_DB_URI
from SANYAMUSIC import app
from motor.motor_asyncio import AsyncIOMotorClient

mongo = AsyncIOMotorClient(MONGO_DB_URI)
antichannel_db = mongo.SANYAMUSIC["antichannel"]

async def is_antichannel_enabled(chat_id: int) -> bool:
    chat = await antichannel_db.find_one({"chat_id": chat_id})
    return chat.get("status", False) if chat else False

async def enable_antichannel(chat_id: int):
    await antichannel_db.update_one({"chat_id": chat_id}, {"$set": {"status": True}}, upsert=True)

async def disable_antichannel(chat_id: int):
    await antichannel_db.update_one({"chat_id": chat_id}, {"$set": {"status": False}}, upsert=True)

# Constants
ANTICHANNEL_GROUP = 10
CHAT_ADMIN_REQUIRED = "**❍ I need to be an admin with ban rights to do this!**"

# Command to toggle antichannel status
@app.on_message(filters.command("antichannel", prefixes=COMMAND_PREFIXES) & filters.group)
async def antichannel_handler(client: Client, message: Message):
    try:
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("You need to be an admin to use this command.")
    except Exception:
        return await message.reply_text("You need to be an admin to use this command.")

    chat_id = message.chat.id

    if await is_antichannel_enabled(chat_id):
        # If already enabled, send a button to disable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❍ 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 ❍", callback_data=f"disable_antichannel:{chat_id}")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="delete")]]
        )
        await message.reply_text("**❍ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖺𝗋𝖾 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
    else:
        # If not enabled, send a button to enable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❍ 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 ❍", callback_data=f"enable_antichannel:{chat_id}")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="delete")]]
             
        )
        await message.reply_text("**❍ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖺𝗋𝖾 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)


# Callback query handler to enable/disable antichannels
@app.on_callback_query(filters.regex("^(enable_antichannel|disable_antichannel):"))
async def toggle_antichannel(client: Client, callback_query):
    try:
        member = await callback_query.message.chat.get_member(callback_query.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await callback_query.answer("Only admins can perform this action.", show_alert=True)
    except Exception:
        return await callback_query.answer("Only admins can perform this action.", show_alert=True)

    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)

    if action == "enable_antichannel":
        await enable_antichannel(chat_id)
        await callback_query.message.edit_text("**❍ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")
    elif action == "disable_antichannel":
        await disable_antichannel(chat_id)
        await callback_query.message.edit_text("**❍ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")

# Manage antichannel logic
@app.on_message(filters.group, group=ANTICHANNEL_GROUP)
async def manage_antichannel(client: Client, message: Message):
    chat_id = message.chat.id

    if not await is_antichannel_enabled(chat_id):
        return

    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return

    # Check if the message is sent using a channel profile
    if message.sender_chat:
        sender_chat = message.sender_chat

        # Check if the channel is linked to the group
        chat = await client.get_chat(chat_id)
        if chat.linked_chat and sender_chat.id == chat.linked_chat.id:
            return

        # Ban the channel and announce it
        try:
            await client.ban_chat_member(chat_id, sender_chat.id)
            await message.reply_text(f"**❍ Channel {sender_chat.title} has been banned.**\n")
        except ChatAdminRequired:
            await message.reply_text(CHAT_ADMIN_REQUIRED)
        except Exception as e:
            await message.reply_text(f"**❍ Failed to ban {sender_chat.title}.**")

__module__ = "𝖠𝗇𝗍𝗂𝖢𝗁𝖺𝗇𝗇𝖾𝗅"
__help__ = "✧ /𝖺𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 : 𝖴𝗌𝖾 𝖨𝗍 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾 𝖮𝗋 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂-𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉.\n(𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖱𝖾𝗆𝗈𝗏𝖾𝗌 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖯𝗋𝗈𝖿𝗂𝗅𝖾𝗌 𝖥𝗋𝗈𝗆 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉)"
