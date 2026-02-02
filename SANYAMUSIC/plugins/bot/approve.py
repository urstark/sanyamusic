import os
from time import time
import asyncio
from typing import Tuple, Union, Optional

from SANYAMUSIC import app
from SANYAMUSIC.core.mongo import mongodb
from SANYAMUSIC.misc import SUDOERS
from pyrogram import enums, filters
from pyrogram.types import (CallbackQuery, ChatJoinRequest,
                            InlineKeyboardButton, InlineKeyboardMarkup, Message)
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------------- #
# Databases
AUTOAPPROVE_DB = mongodb.autoapprove
APPROVEMSG_DB = mongodb.approvemsg
APPROVECOUNT_DB = mongodb.approvecounter

# In-memory counter for performance
INMEM_COUNTERS = {}

# Anti-spam settings
SPAM_WINDOW_SECONDS = 60
SPAM_THRESHOLD = 10

# Image assets
bg_path = "SANYAMUSIC/assets/userinfo.png"
font_path = "SANYAMUSIC/assets/hiroko.ttf"

# Welcome message text (can be overridden by env var)
TEXT = os.environ.get(
    "APPROVED_WELCOME_TEXT",
    "**❅─────✧❅✦❅✧─────❅**\n**🥀ʜᴇʏ {mention}**\n\n**🏓ᴡᴇʟᴄᴏᴍᴇ ɪɴ ɴᴇᴡ ɢʀᴏᴜᴘ✨**\n\n**➻** {title}\n\n**💞ɴᴏᴡ ᴍᴀᴋᴇ ɴᴇᴡ ғʀɪᴇɴᴅs ᴀɴᴅ sᴛᴀʏ ᴀʟᴡᴀʏs ᴏɴʟɪɴᴇ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ🥳**\n**❅─────✧❅✦❅✧─────❅**"
)

# --------------------------------------------------------------------------------- #
# Image Generation Logic from the old bot/approve.py

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None,
):
    bg = Image.open(bg_path)

    if profile_path:
        try:
            img = Image.open(profile_path)
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

            circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
            circular_img.paste(img, (0, 0), mask)
            resized = circular_img.resize((400, 400))
            bg.paste(resized, (440, 160), resized)
        except Exception:
            pass

    img_draw = ImageDraw.Draw(bg)
    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )
    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #
# Helper functions from the old tools/approve.py

async def delete_message_after(message: Message, delay: int):
    """Deletes a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        # Bot might not have delete permissions, or message already deleted.
        print(f"Could not delete message {message.id} in chat {message.chat.id}: {e}")

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

def small(text: str) -> str:
    small_caps_map = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZᴀʙᴄᴅᴇғɢʜɪJᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
    )
    return text.translate(small_caps_map)

async def load_counter_from_db(chat_id: int) -> Tuple[int, float, int]:
    rec = await APPROVECOUNT_DB.find_one({"chat_id": chat_id})
    now = time()
    if not rec:
        await APPROVECOUNT_DB.update_one(
            {"chat_id": chat_id},
            {"$set": {"count": 0, "window_start": now, "disables": 0}},
            upsert=True,
        )
        return 0, now, 0
    return rec.get("count", 0), rec.get("window_start", now), rec.get("disables", 0)

async def save_counter_to_db(chat_id: int, count: int, window_start: float, disables: int):
    await APPROVECOUNT_DB.update_one(
        {"chat_id": chat_id},
        {"$set": {"count": count, "window_start": window_start, "disables": disables}},
        upsert=True,
    )

async def send_welcome_message(chat, user):
    photo_path = None
    welcome_photo = None
    sent_message = None
    try:
        if user.photo:
            photo_path = await app.download_media(user.photo.big_file_id)
        
        welcome_photo = await get_userinfo_img(
            bg_path=bg_path,
            font_path=font_path,
            user_id=user.id,
            profile_path=photo_path,
        )
        
        sent_message = await app.send_photo(
            chat_id=chat.id,
            photo=welcome_photo,
            caption=TEXT.format(mention=user.mention, title=chat.title),
        )
    except Exception as e:
        print(f"[Approve Welcome Error]: {e}")
        # Fallback to text message if image fails
        sent_message = await app.send_message(chat.id, f"<blockquote><b> {small('Request Approved')}</b>\n👤 <a href='tg://user?id={user.id}'>{user.first_name}</a></blockquote>")
    finally:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
        if welcome_photo and os.path.exists(welcome_photo):
            os.remove(welcome_photo)

        if sent_message:
            asyncio.create_task(delete_message_after(sent_message, 15))

# --------------------------------------------------------------------------------- #
# Command Handlers

@app.on_message(filters.command("autoapprove") & filters.group)
async def autoapprove_cmd(_, m: Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("<blockquote><b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ.</b></blockquote>")
    if len(m.command) < 2:
        return await m.reply_text("<blockquote><b>ᴜꜱᴇ:</b> /autoapprove on | off</blockquote>")
    mode = m.command[1].lower()
    if mode in ["on", "yes", "enable"]:
        await AUTOAPPROVE_DB.update_one({"chat_id": m.chat.id}, {"$set": {"enabled": True}}, upsert=True)
        await m.reply_text(f"<blockquote><b> {small('Auto Approve Enabled')}</b></blockquote>")
    elif mode in ["off", "no", "disable"]:
        await AUTOAPPROVE_DB.update_one({"chat_id": m.chat.id}, {"$set": {"enabled": False}}, upsert=True)
        await m.reply_text(f"<blockquote><b> {small('Auto Approve Disabled')}</b></blockquote>")
    else:
        await m.reply_text("<blockquote><b>ᴜꜱᴇ:</b> /autoapprove on | off</blockquote>")

@app.on_message(filters.command("approve") & filters.group)
async def approve_msg_cmd(_, m: Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("<blockquote><b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ.</b></blockquote>")
    if len(m.command) < 2:
        return await m.reply_text("<blockquote><b>ᴜꜱᴇ:</b> /approve on | off</blockquote>")
    mode = m.command[1].lower()
    if mode in ["on", "yes", "enable"]:
        await APPROVEMSG_DB.update_one({"chat_id": m.chat.id}, {"$set": {"enabled": True}}, upsert=True)
        await m.reply_text(f"<blockquote><b> {small('Approve Message Enabled')}</b></blockquote>")
    elif mode in ["off", "no", "disable"]:
        await APPROVEMSG_DB.update_one({"chat_id": m.chat.id}, {"$set": {"enabled": False}}, upsert=True)
        await m.reply_text(f"<blockquote><b> {small('Approve Message Disabled')}</b></blockquote>")
    else:
        await m.reply_text("<blockquote><b>ᴜꜱᴇ:</b> /approve on | off</blockquote>")

@app.on_chat_join_request(filters.group | filters.channel)
async def join_request_handler(_, req: ChatJoinRequest):
    chat, user = req.chat, req.from_user
    
    auto_doc = await AUTOAPPROVE_DB.find_one({"chat_id": chat.id}) or {"enabled": False}
    auto_enabled = auto_doc.get("enabled", False)

    if auto_enabled:
        try:
            await app.approve_chat_join_request(chat.id, user.id)
            approve_msg_doc = await APPROVEMSG_DB.find_one({"chat_id": chat.id}) or {"enabled": True}
            approve_msg_enabled = approve_msg_doc.get("enabled", True)
            if approve_msg_enabled:
                await send_welcome_message(chat, user)
        except Exception as e:
            print(f"[Auto-Approve Error]: {e}")
        return

    now = time()
    mem = INMEM_COUNTERS.get(chat.id)
    if mem:
        count, window_start = mem
    else:
        db_count, db_window_start, db_disables = await load_counter_from_db(chat.id)
        count, window_start = db_count, db_window_start
        INMEM_COUNTERS[chat.id] = (count, window_start)

    if now - window_start > SPAM_WINDOW_SECONDS:
        count, window_start = 0, now

    count += 1
    INMEM_COUNTERS[chat.id] = (count, window_start)
    _, _, disables = await load_counter_from_db(chat.id)
    await save_counter_to_db(chat.id, count, window_start, disables)

    if count >= SPAM_THRESHOLD:
        await APPROVEMSG_DB.update_one({"chat_id": chat.id}, {"$set": {"enabled": False}}, upsert=True)
        disables += 1
        INMEM_COUNTERS[chat.id] = (0, now)
        await save_counter_to_db(chat.id, 0, now, disables)
        try:
            await app.send_message(
                chat.id,
                f"<blockquote><b> {small('Approve Auto-Disabled')}</b>\n"
                f"{small('Too many join requests detected — approve messages turned OFF automatically.')}\n\n"
                f"<b> Auto-Disable Count:</b> {disables}</blockquote>",
            )
        except:
            pass
        return

    try:
        await app.send_message(
            chat.id,
            f"<b>{small('𝑁𝑒𝑤 𝑗𝑜𝑖𝑛 𝑅𝑒𝑞𝑢𝑒𝑠𝑡')}</b>\n\n"
            "❍ <b>𝑈𝑠𝑒𝑟 𝑖𝑛𝑓𝑜</b>\n\n"
            f":⧽ 𝑛𝑎𝑚𝑒: <b>{user.first_name}</b>\n"
            f":⧽ 𝑢𝑠𝑒𝑟: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
            f":⧽ 𝑖𝑑: <code>{user.id}</code>",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(" 𝐴𝑐𝑐𝑒𝑝𝑡", callback_data=f"acc_{user.id}_{chat.id}"),
                    InlineKeyboardButton(" 𝐷𝑖𝑠𝑚𝑖𝑠𝑠", callback_data=f"dis_{user.id}_{chat.id}"),
                ]]
            ),
        )
    except:
        pass

@app.on_callback_query(filters.regex("^acc_"))
async def approve_btn(_, cq: CallbackQuery):
    try:
        parts = cq.data.split("_")
        user_id, chat_id = int(parts[1]), int(parts[2])
    except:
        return await cq.answer("Invalid data.", show_alert=True)

    if not await is_admin(chat_id, cq.from_user.id):
        return await cq.answer("Only group admins/owner can approve.", show_alert=True)

    try:
        await app.approve_chat_join_request(chat_id, user_id)
        await cq.message.delete()
        
        approve_msg_doc = await APPROVEMSG_DB.find_one({"chat_id": chat_id}) or {"enabled": True}
        if approve_msg_doc.get("enabled", True):
            user = await app.get_users(user_id)
            chat = await app.get_chat(chat_id)
            await send_welcome_message(chat, user)
        
        await cq.answer("Approved Successfully!")
    except Exception as e:
        print(f"[Manual Approve Error]: {e}")
        await cq.answer("Error Approving!", show_alert=True)

@app.on_callback_query(filters.regex("^dis_"))
async def dismiss_btn(_, cq: CallbackQuery):
    try:
        parts = cq.data.split("_")
        user_id, chat_id = int(parts[1]), int(parts[2])
    except:
        return await cq.answer("Invalid data.", show_alert=True)

    if not await is_admin(chat_id, cq.from_user.id):
        return await cq.answer("Only group admins/owner can dismiss.", show_alert=True)

    try:
        await app.decline_chat_join_request(chat_id, user_id)
        await cq.message.edit(f"<blockquote><b> {small('Request Dismissed')}</b></blockquote>")
        await cq.answer("Dismissed!")
    except:
        await cq.answer("Error!", show_alert=True)

@app.on_message(filters.command(["approvestatus", "approveinfo"]) & filters.group)
async def approvestatus_cmd(_, m: Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("<blockquote><b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ.</b></blockquote>")

    auto_doc = await AUTOAPPROVE_DB.find_one({"chat_id": m.chat.id}) or {"enabled": False}
    approve_doc = await APPROVEMSG_DB.find_one({"chat_id": m.chat.id}) or {"enabled": True}
    count, _, disables = await load_counter_from_db(m.chat.id)

    auto_status = "ON" if auto_doc.get("enabled", False) else "OFF"
    approve_status = "ON" if approve_doc.get("enabled", True) else "OFF"

    await m.reply_text(
        f"<blockquote><b>{small('APPROVE SYSTEM STATUS')}</b>\n\n"
        f"<b>Chat:</b> {m.chat.title}\n"
        f"<b>Chat ID:</b> <code>{m.chat.id}</code>\n\n"
        f"<b>Auto Approve:</b> {auto_status}\n"
        f"<b>Approve Message:</b> {approve_status}\n\n"
        f"<b>Current Window Count:</b> {count}\n"
        f"<b>Auto-Disable Count:</b> {disables}\n\n"
        f"<b>Commands:</b> /autoapprove on|off  •  /approve on|off</blockquote>"
    )

@app.on_message(filters.command(["globalapprovestatus", "globalapprove"]) & filters.user([user.id if hasattr(user, 'id') else user for user in SUDOERS]) & ~filters.group)
async def global_approvestatus_cmd(_, m: Message):
    auto_map = {doc["chat_id"]: doc.get("enabled", False) async for doc in AUTOAPPROVE_DB.find({})}
    approve_map = {doc["chat_id"]: doc.get("enabled", True) async for doc in APPROVEMSG_DB.find({})}
    all_chat_ids = set(list(auto_map.keys()) + list(approve_map.keys()))

    if not all_chat_ids:
        return await m.reply_text("<blockquote><b>No chats found in DB.</b></blockquote>")

    lines = [f"<blockquote><b>{small('GLOBAL APPROVE STATUS')}</b>\n"]
    for cid in sorted(all_chat_ids):
        try:
            chat = await app.get_chat(cid)
            title = getattr(chat, "title", str(cid))
        except:
            title = str(cid)
        a_status = "ON" if auto_map.get(cid, False) else "OFF"
        p_status = "ON" if approve_map.get(cid, True) else "OFF"
        lines.append(f"• {title} — <code>{cid}</code>\n  Auto: {a_status}  •  ApproveMsg: {p_status}\n")

    lines.append("</blockquote>")
    await m.reply_text("\n".join(lines))

@app.on_message(filters.command("approve_reset_counter") & filters.group)
async def approve_reset_counter_cmd(_, m: Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("<blockquote><b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ.</b></blockquote>")
    await save_counter_to_db(m.chat.id, 0, time(), 0)
    INMEM_COUNTERS.pop(m.chat.id, None)
    await m.reply_text("<blockquote><b> Counter reset for this chat.</b></blockquote>")

@app.on_message(filters.command("approveall") & filters.group)
async def approve_all_cmd(_, m: Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("<blockquote><b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ.</b></blockquote>")
    try:
        reqs = [req async for req in app.get_chat_join_requests(m.chat.id)]
    except Exception as e:
        return await m.reply_text(f"<blockquote><b> ᴄᴀɴ'ᴛ ꜰᴇᴛᴄʜ ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇꜱᴛꜱ.</b>\nError: {e}</blockquote>")

    if not reqs:
        return await m.reply_text("<blockquote><b> ɴᴏ ᴘᴇɴᴅɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇꜱᴛꜱ.</b></blockquote>")

    approved, failed = 0, 0
    for req in reqs:
        try:
            await app.approve_chat_join_request(m.chat.id, req.from_user.id)
            approved += 1
        except:
            failed += 1
    
    await m.reply_text(
        f"<blockquote>"
        f"<b>{small('Approve All Summary')}</b>\n\n"
        f"{small('Total Requests')}: <b>{len(reqs)}</b>\n"
        f"{small('Approved Successfully')}: <b>{approved}</b>\n"
        f"{small('Failed to Approve')}: <b>{failed}</b>"
        f"</blockquote>"
    )
