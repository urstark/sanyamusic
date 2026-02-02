import random
from typing import Union

from pyrogram import filters, types
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from SANYAMUSIC import app
from SANYAMUSIC.utils.database import get_lang
from SANYAMUSIC.utils.decorators.language import LanguageStart, languageCB
from SANYAMUSIC.utils.inline.help import help_back_markup, private_help_panel, help_pannel, help_category_pannel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string
from SANYAMUSIC.utils.stuffs.helper import Helper


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def helper_private(client, message: Message, _):
    try:
        await message.delete()
    except:
        pass
    keyboard = help_pannel(_, True)
    await message.reply_text(
        _["help_1"].format(SUPPORT_CHAT),
        reply_markup=keyboard,
    )

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("open_help_panel") & ~BANNED_USERS)
@languageCB
async def open_help_panel_cb(client, callback_query: CallbackQuery, _):
    try:
        await callback_query.answer()
    except:
        pass
    keyboard = help_pannel(_, True)
    await callback_query.edit_message_text(
        _["help_1"].format(SUPPORT_CHAT),
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, callback_query: CallbackQuery, _):
    callback_data = callback_query.data.strip()
    parts = callback_data.split()
    cb = parts[1]
    category = parts[2] if len(parts) > 2 else "music"
    keyboard = help_back_markup(_, category)
    help_text = {
        "hb1": Helper.HELP_1, "hb2": Helper.HELP_2, "hb3": Helper.HELP_3,
        "hb4": Helper.HELP_4, "hb5": Helper.HELP_5, "hb6": Helper.HELP_6,
        "hb7": Helper.HELP_7, "hb8": Helper.HELP_8, "hb9": Helper.HELP_9,
        "hb10": Helper.HELP_10, "hb11": Helper.HELP_11, "hb12": Helper.HELP_12,
        "hb13": Helper.HELP_13, "hb14": Helper.HELP_14, "hb15": Helper.HELP_15,
        "hb16": Helper.HELP_16, "hb17": Helper.HELP_17, "hb18": Helper.HELP_18,
        "hb19": Helper.HELP_19, "hb20": Helper.HELP_20, "hb21": Helper.HELP_21,
        "hb22": Helper.HELP_22, "hb23": Helper.HELP_23, "hb24": Helper.HELP_24,
        "hb25": Helper.HELP_25, "hb26": Helper.HELP_26, "hb27": Helper.HELP_27,
        "hb28": Helper.HELP_28, "hb29": Helper.HELP_29, "hb30": Helper.HELP_30,
        "hb31": Helper.HELP_31, "hb32": Helper.HELP_32, "hb33": Helper.HELP_33,
        "hb34": Helper.HELP_34, "hb35": Helper.HELP_35,
        "hb36": Helper.HELP_36, "hb37": Helper.HELP_37, "hb38": Helper.HELP_38,
        "hb39": Helper.HELP_39, "hb40": Helper.HELP_40, "hb41": Helper.HELP_41,
        "hb42": Helper.HELP_42, "hb43": Helper.HELP_43, "hb44": Helper.HELP_44,
        "hb45": Helper.HELP_45, "hb46": Helper.HELP_46, "hb47": Helper.HELP_47,
        "hb48": Helper.HELP_48, "hb49": Helper.HELP_49, "hb50": Helper.HELP_50,
        "hb51": Helper.HELP_51, "hb52": Helper.HELP_52, "hb53": Helper.HELP_53,
        "hb54": Helper.HELP_54, "hb55": Helper.HELP_55,
    }
    if cb in help_text:
        await callback_query.edit_message_text(help_text[cb], reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"help_category (\w+)"))
@languageCB
async def help_category_handler(client, callback_query: CallbackQuery, _):
    category = callback_query.matches[0].group(1)
    keyboard = help_category_pannel(_, category)
    try:
        await callback_query.answer()
    except:
        pass
    await callback_query.edit_message_text(
        _["help_1"].format(SUPPORT_CHAT),
        reply_markup=keyboard
    )
