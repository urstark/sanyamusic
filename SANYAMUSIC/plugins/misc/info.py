import asyncio, os, time, aiohttp
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from asyncio import sleep
from SANYAMUSIC import app
from pyrogram import filters, Client, enums
from pyrogram.enums import ParseMode
from pyrogram.types import *
from typing import Union, Optional
import random

# --------------------------------------------------------------------------------- #
# CONFIGURATION & ASSETS
# --------------------------------------------------------------------------------- #

bg_path = "SANYAMUSIC/assets/userinfo.png"
font_path = "SANYAMUSIC/assets/hiroko.ttf"
DEFAULT_PROFILE_IMAGE = "SANYAMUSIC/assets/upic.png" 

INFO_TEXT = """**
[ᯤ] 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗡𝗧𝗢𝗡 [ᯤ]

[🍹] ᴜsᴇʀ ɪᴅ ‣ **`{}`
**[💓] ғɪʀsᴛ ɴᴀᴍᴇ ‣ **{}
**[💗] ʟᴀsᴛ ɴᴀᴍᴇ ‣ **{}
**[🍷] ᴜsᴇʀɴᴀᴍᴇ ‣ **`{}`
**[🍬] ᴍᴇɴᴛɪᴏɴ ‣ **{}
**[🍁] ʟᴀsᴛ sᴇᴇɴ ‣ **{}
**[🎫] ᴅᴄ ɪᴅ ‣ **{}
**[🗨️] ʙɪᴏ ‣ **`{}`

**☉━━☉━━☉━侖━☉━━☉━━☉**
"""

# --------------------------------------------------------------------------------- #
# UTILITY FUNCTIONS
# --------------------------------------------------------------------------------- #

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],    
    profile_path: str
):
    bg = Image.open(bg_path)

    # Open the .jpg file and convert to RGBA to support transparency masking
    img = Image.open(profile_path).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

    circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    circular_img.paste(img, (0, 0), mask)
    resized = circular_img.resize((400, 400))
    bg.paste(resized, (440, 160), resized)

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

async def userstatus(user_id):
   try:
      user = await app.get_users(user_id)
      x = user.status
      if x == enums.UserStatus.RECENTLY:
         return "Recently."
      elif x == enums.UserStatus.LAST_WEEK:
          return "Last week."
      elif x == enums.UserStatus.LONG_AGO:
          return "Long time ago."
      elif x == enums.UserStatus.OFFLINE:
          return "Offline."
      elif x == enums.UserStatus.ONLINE:
         return "Online."
   except:
        return "**sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ʜᴀᴘᴘᴇɴᴇᴅ !**"

# --------------------------------------------------------------------------------- #
# COMMAND HANDLER
# --------------------------------------------------------------------------------- #

@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]))
async def userinfo(_, message):
    chat_id = message.chat.id
    
    if not message.reply_to_message and len(message.command) == 2:
        user_id = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.from_user.id

    try:
        user_info = await app.get_chat(user_id)
        user = await app.get_users(user_id)
        
        status = await userstatus(user.id)
        id = user_info.id
        dc_id = user.dc_id
        first_name = user_info.first_name 
        last_name = user_info.last_name if user_info.last_name else "No last name"
        username = user_info.username if user_info.username else "No Username"
        mention = user.mention
        bio = user_info.bio if user_info.bio else "No bio set"

        # Generate Image using the hardcoded .jpg file
        final_img_path = await get_userinfo_img(
            bg_path=bg_path,
            font_path=font_path,
            user_id=user.id,
            profile_path=DEFAULT_PROFILE_IMAGE,
        )
            
        await app.send_photo(
            chat_id, 
            photo=final_img_path, 
            caption=INFO_TEXT.format(id, first_name, last_name, username, mention, status, dc_id, bio), 
            reply_to_message_id=message.id
        )

        if os.path.exists(final_img_path):
            os.remove(final_img_path)

    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ:** `{str(e)}`")

