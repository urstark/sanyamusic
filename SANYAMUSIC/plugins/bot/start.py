import asyncio
import aiohttp
import random
import time
from pyrogram import filters
from pyrogram.enums import ChatType, ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
import config
from SANYAMUSIC import app
from SANYAMUSIC.misc import _boot_
from SANYAMUSIC.plugins.sudo.sudoers import sudoers_list
from SANYAMUSIC.utils import bot_sys_stats
from SANYAMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from SANYAMUSIC.utils.decorators.language import LanguageStart
from SANYAMUSIC.utils.formatters import get_readable_time
from SANYAMUSIC.utils.inline import help_pannel, private_panel, start_panel
from strings import get_string
from config import BANNED_USERS

# Assets 
STICKER = [
    "CAACAgUAAx0CYlaJawABBy4vZaieO6T-Ayg3mD-JP-f0yxJngIkAAv0JAALVS_FWQY7kbQSaI-geBA",
    "CAACAgUAAx0CYlaJawABBy4jZaidvIXNPYnpAjNnKgzaHmh3cvoAAiwIAAIda2lVNdNI2QABHuVVHgQ",
    "CAACAgUAAxkBAAIBGWlPj2BophzDt6BnmyBS-NFtqg7XAAJ9EgACKim5VpulXSTMVLgrHgQ",
    "CAACAgUAAyEFAATKMLw9AAICtWlPj7tZxFmYVV_Ut4V9P1p2-3geAAIKDwACNyvhV0CesVynrgRUHgQ",
    "CAACAgUAAyEFAATKMLw9AAICtmlPj7sZ0HT2Rd3D1UqkzS3emXViAAJnDQACNIDgV5xhBUdt_f_OHgQ",
    "CAACAgUAAyEFAATKMLw9AAICt2lPj7u8HsJsaYzz7Ckcp050XNjUAALHDgACMBngVxP0ZbLYPzrdHgQ",
    "CAACAgUAAyEFAATKMLw9AAICvmlPj-rhVaQNL8BTBogN-zLj8tsJAAIeEQACa-ZBV7VQQVNCHMhKHgQ",
    "CAACAgUAAyEFAATKMLw9AAICwWlPkAp5D4ZAIfo5fO_GMUOhaYUUAAKaEQAC88upV61z2KeqfHoOHgQ",
]

EMOJIOS = ["❤️", "😁", "👀", "⚡️", "🕊", "❤️‍🔥", "💅", "👻",]

SHASHANK_IMG = [
    "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
    "https://graph.org/file/69ba894371860cd22d92e.jpg",
    "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
    "https://graph.org/file/3a400f1f32fc381913061.jpg",
    "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
    "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
    "https://graph.org/file/25e215c4602b241b66829.jpg",
    "https://graph.org/file/a13e9733afdad69720d67.jpg",
    "https://graph.org/file/692e89f8fe20554e7a139.jpg",
    "https://graph.org/file/db277a7810a3f65d92f22.jpg",
    "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
    "https://graph.org/file/f86b71018196c5cfe7344.jpg",
    "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
    "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
    "https://graph.org/file/84de4b440300297a8ecb3.jpg",
    "https://graph.org/file/84e84ff778b045879d24f.jpg",
    "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
    "https://graph.org/file/df11d8257613418142063.jpg",
    "https://graph.org/file/9e23720fedc47259b6195.jpg",
    "https://graph.org/file/826485f2d7db6f09db8ed.jpg",
    "https://graph.org/file/ff3ad786da825b5205691.jpg",
    "https://graph.org/file/52713c9fe9253ae668f13.jpg",
    "https://graph.org/file/8f8516c86677a8c91bfb1.jpg",
    "https://graph.org/file/6603c3740378d3f7187da.jpg"
]

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 1. Reaction to the User's message
    try:
        await message.react(random.choice(EMOJIOS))
    except:
        pass

    # 2. Set Bot Status to Typing
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    # 4. Layer 2: Separate "Starting" Message
    starting_msg = await message.reply_text("**__𝐻𝑖𝑒𝑒 𝐶𝑢𝑡𝑖𝑒𝑒𝑠 ‹𝟹__**")
    await asyncio.sleep(0.6) 
    await starting_msg.delete()

    # 5. Send Random Sticker
    umm = await message.reply_sticker(sticker=random.choice(STICKER))
    await asyncio.sleep(0.6)
    await umm.delete()

    # 6. Main Start Logic (Deep Links)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            await message.reply_photo(
                random.choice(SHASHANK_IMG),
                caption=_['help_1'].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"❍ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>๏ ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>๏ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
        elif name.startswith("inf"):
            query = name.replace("info_", "", 1)
            results = VideosSearch(query, limit=1)

            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(title, duration, views, published, channellink, channel, app.mention)
            key = InlineKeyboardMarkup([[
                InlineKeyboardButton(text=_["S_B_8"], url=link),
                InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
            ]])
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
    else:
        # Standard Main Start Panel
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        
        await message.reply_photo(
            random.choice(SHASHANK_IMG),
            caption=_["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM, served_users, served_chats),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"❍ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>๏ ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>๏ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(SHASHANK_IMG),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    random.choice(SHASHANK_IMG),
                    caption=_["start_3"].format(message.from_user.mention, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)

@app.on_callback_query(filters.regex("api_status"))
async def api_status_callback(client, query):
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(config.HEALTH_API_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    ping = int((end_time - start_time) * 1000)
                    
                    is_ok = data.get("status") == "ok"
                    yt_status = "ʀᴇsᴘᴏɴsɪᴠᴇ" if is_ok else "ᴜɴʀᴇsᴘᴏɴsɪᴠᴇ"
                    footer = "ᴇᴠᴇʀʏᴛʜɪɴɢ ʟᴏᴏᴋs ɢᴏᴏᴅ!" if is_ok else "ɪssᴜᴇs ᴅᴇᴛᴇᴄᴛᴇᴅ!"

                    text = (
                        "💌 ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ sᴛᴀᴛᴜs...\n\n"
                        "❍ ᴅᴀᴛᴀʙᴀsᴇ: ᴏɴʟɪɴᴇ\n"
                        f"❍ ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ: {yt_status}\n"
                        "❍ ʙᴏᴛ sᴇʀᴠᴇʀ: ʀᴜɴɴɪɴɢ sᴍᴏᴏᴛʜʟʏ\n"
                        "❍ ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ: ᴏᴘᴛɪᴍᴀʟ\n"
                        f"❍ ᴀᴘɪ ᴘɪɴɢ: {ping/10:.1f} ᴍs\n\n"
                        f"{footer}"
                    )
                    await query.answer(text, show_alert=True)
                else:
                    await query.answer("ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀᴘɪ sᴛᴀᴛᴜs.", show_alert=True)
    except Exception:
        await query.answer("ғᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀᴘɪ.", show_alert=True)
