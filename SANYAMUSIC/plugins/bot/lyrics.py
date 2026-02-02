import os
import random
import re
import string

import lyricsgenius as lg
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from SANYAMUSIC import app
from SANYAMUSIC.utils.decorators.language import language # <--- Imported decorator

from config import BANNED_USERS, lyrical

# Hardcode the Genius API key.
api_key = "fcXGwudRZTE8zdMOYKNMoRGIWfBjca_4s5wF5keHeCTd68yURmceO4MGhAbyx-qp"

# if not api_key:
#     raise ValueError("GENIUS_ACCESS_TOKEN environment variable not set. Please set your Genius API key.")

y = lg.Genius(
    api_key,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True,
)
y.verbose = False

# --- END MODIFIED SECTION ---

@app.on_message(filters.command(["lyrics"]) & ~BANNED_USERS)
@language # <--- FIX 1: Apply the imported language decorator
async def lrsearch(client, message: Message, _): # <--- FIX 2: Add '_' argument for localization
    if len(message.command) < 2:
        return await message.reply_text(_["lyrics_1"])

    title = message.text.split(None, 1)[1]
    m = await message.reply_text(_["lyrics_2"])
    
    S = y.search_song(title, get_full_info=False)
    if S is None:
        return await m.edit(_["lyrics_3"].format(title))

    ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    lyric = S.lyrics
    if "Embed" in lyric:
        lyric = re.sub(r"\d*Embed", "", lyric)
    lyrical[ran_hash] = lyric

    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["L_B_1"],
                    url=f"https://t.me/{app.username}?start=lyrics_{ran_hash}",
                ),
            ]
        ]
    )
    
    await m.edit(_["lyrics_4"], reply_markup=upl)
