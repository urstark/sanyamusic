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

STARK_IMG = [
    "https://files.catbox.moe/k43ugw.jpg",
    "https://files.catbox.moe/9soc53.jpg",
    "https://files.catbox.moe/k8vvww.jpg",
    "https://files.catbox.moe/bag4i1.jpg",
    "https://files.catbox.moe/by685a.jpg",
    "https://files.catbox.moe/f7xoqs.jpg",
    "https://files.catbox.moe/5wqxf5.jpg",
    "https://files.catbox.moe/431fr0.jpg",
    "https://files.catbox.moe/ue0jdr.jpg",
    "https://files.catbox.moe/w3ul6m.jpg",
    "https://files.catbox.moe/tb5lbj.jpg",
    "https://files.catbox.moe/gntxjn.jpg",
    "https://files.catbox.moe/c6msne.jpg",
    "https://files.catbox.moe/pivnj5.jpg",
    "https://files.catbox.moe/zvl3zg.jpg",
    "https://files.catbox.moe/geb29n.jpg",
    "https://files.catbox.moe/59i2eq.jpg",
    "https://files.catbox.moe/98frng.jpg",
    "https://files.catbox.moe/cdsc73.jpg",
    "https://files.catbox.moe/fhyuem.jpg",
    "https://files.catbox.moe/4wdkm1.jpg",
    "https://files.catbox.moe/083llp.jpg",
    "https://files.catbox.moe/8h4rha.jpg",
    "https://files.catbox.moe/7bckxd.jpg",
    "https://graph.org/file/6603c3740378d3f7187da.jpg",
    "https://files.catbox.moe/3sbjl5.jpg"
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
    starting_msg = await message.reply_text("**__𝐻𝑖𝑒𝑒 𝐶𝑢𝑡𝑖𝑒𝑒 __**")
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
                random.choice(STARK_IMG),
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
            random.choice(STARK_IMG),
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
        random.choice(STARK_IMG),
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
                    random.choice(STARK_IMG),
                    caption=_["start_3"].format(message.from_user.mention, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)



