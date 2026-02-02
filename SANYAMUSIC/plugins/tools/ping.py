
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import *
from SANYAMUSIC import app
from SANYAMUSIC.core.call import SANYA
from SANYAMUSIC.utils import bot_sys_stats
from SANYAMUSIC.utils.decorators.language import language
from SANYAMUSIC.utils.inline import supp_markup
from config import BANNED_USERS
import random

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


@app.on_message(filters.command("ping", prefixes=["/", ""]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_photo(
        random.choice(STARK_IMG),
        caption=_["ping_1"].format(app.mention),
    )
    pytgping = await SANYA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )
