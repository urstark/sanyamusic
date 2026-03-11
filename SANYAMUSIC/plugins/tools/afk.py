import time, re, asyncio
from config import BOT_USERNAME
from pyrogram.enums import MessageEntityType
from pyrogram import filters
from pyrogram.types import Message
from SANYAMUSIC import app
from SANYAMUSIC.utils.formatters import get_readable_time
from SANYAMUSIC.mongo.afkdb import add_afk, is_afk, remove_afk

# Helper function to delete AFK messages after 15 seconds
async def auto_delete_afk(msg, delay=15):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

async def send_afk_msg(message, user_name, user_id, reasondb, is_wake_up=False):
    """Universal helper to send AFK status or wake-up message."""
    try:
        afktype = reasondb["type"]
        timeafk = reasondb["time"]
        data = reasondb["data"]
        reasonafk = reasondb["reason"]
        seenago = get_readable_time((int(time.time() - timeafk)))

        status = "ɪs ᴀғᴋ sɪɴᴄᴇ" if not is_wake_up else "ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ"
        caption = f"**{user_name[:25]}** {status} {seenago}"
        if reasonafk:
            caption += f"\n\nʀᴇᴀsᴏɴ: `{reasonafk}`"

        if afktype == "text" or afktype == "text_reason":
            msg = await message.reply_text(caption, disable_web_page_preview=True)
        elif afktype == "animation":
            msg = await message.reply_animation(data, caption=caption)
        elif afktype == "photo":
            msg = await message.reply_photo(photo=f"downloads/{user_id}.jpg", caption=caption)
        else:
            msg = await message.reply_text(f"**{user_name[:25]}** {status} {seenago}")
        
        asyncio.create_task(auto_delete_afk(msg))
    except Exception:
        msg = await message.reply_text(f"**{user_name[:25]}** {'ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ' if is_wake_up else 'ɪs ᴀғᴋ'}")
        asyncio.create_task(auto_delete_afk(msg))

@app.on_message(filters.command(["afk", "brb"], prefixes=["/", "!"]))
async def active_afk(_, message: Message):
    if message.sender_chat:
        return
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        await send_afk_msg(message, user_name, user_id, reasondb, is_wake_up=True)

    if len(message.command) == 1 and not message.reply_to_message:
        details = {"type": "text", "time": time.time(), "data": None, "reason": None}
    elif len(message.command) > 1 and not message.reply_to_message:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {"type": "text_reason", "time": time.time(), "data": None, "reason": _reason}
    elif message.reply_to_message:
        reply = message.reply_to_message
        _reason = (message.text.split(None, 1)[1].strip())[:100] if len(message.command) > 1 else None
        if reply.animation:
            details = {"type": "animation", "time": time.time(), "data": reply.animation.file_id, "reason": _reason}
        elif reply.photo:
            await app.download_media(reply, file_name=f"{user_id}.jpg")
            details = {"type": "photo", "time": time.time(), "data": None, "reason": _reason}
        elif reply.sticker:
            if reply.sticker.is_animated:
                details = {"type": "text", "time": time.time(), "data": None, "reason": _reason}
            else:
                await app.download_media(reply, file_name=f"{user_id}.jpg")
                details = {"type": "photo", "time": time.time(), "data": None, "reason": _reason}
        else:
            details = {"type": "text", "time": time.time(), "data": None, "reason": _reason}
    else:
        details = {"type": "text", "time": time.time(), "data": None, "reason": None}

    await add_afk(user_id, details)    
    send = await message.reply_text(f"**{user_name}** ɪs ɴᴏᴡ ᴀғᴋ!")
    asyncio.create_task(auto_delete_afk(send))

chat_watcher_group = 1

@app.on_message(~filters.me & ~filters.bot & ~filters.via_bot, group=chat_watcher_group)
async def chat_watcher_func(_, message):
    if message.sender_chat or not message.from_user:
        return
    
    userid = message.from_user.id
    user_name = message.from_user.first_name

    # Check if the sender is AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        # Prevent waking up if the current message is an AFK command
        is_afk_cmd = False
        if message.text or message.caption:
            msg_check = message.text or message.caption
            if msg_check.startswith(("/", "!")):
                parts = msg_check.split()
                if parts and parts[0][1:].lower() in ["afk", "brb", "ye"]:
                    is_afk_cmd = True
        
        if not is_afk_cmd:
            await remove_afk(userid)
            await send_afk_msg(message, user_name, userid, reasondb, is_wake_up=True)

    # Check for mentions or replies to AFK users
    afk_replied_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        afk_replied_id = message.reply_to_message.from_user.id
        v, r = await is_afk(afk_replied_id)
        if v:
            await send_afk_msg(message, message.reply_to_message.from_user.first_name, afk_replied_id, r)

    if message.entities:
        for ent in message.entities:
            uid = None
            if ent.type == MessageEntityType.MENTION:
                try:
                    user = await app.get_users(message.text[ent.offset : ent.offset + ent.length])
                    uid = user.id
                except:
                    continue
            elif ent.type == MessageEntityType.TEXT_MENTION:
                uid = ent.user.id
            
            if uid and uid != afk_replied_id:
                v, r = await is_afk(uid)
                if v:
                    try:
                        u = ent.user or await app.get_users(uid)
                        await send_afk_msg(message, u.first_name, uid, r)
                    except:
                        pass


