
from pyrogram import filters
import asyncio
import pyfiglet 
from random import choice
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.handlers import MessageHandler
from SANYAMUSIC import app

def figle(text):
    x = pyfiglet.FigletFont.getFonts()
    font = choice(x)
    figled = str(pyfiglet.figlet_format(text,font=font))
    # Pass the text to the callback_data
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ", callback_data=f"figlet_change:{text}"), InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close_reply")]])
    return figled, keyboard

@app.on_message(filters.command("figlet"))
async def echo(bot, message):
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("Example:\n\n`/figlet STARK `")

    kul_text, keyboard = figle(text)
    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{kul_text}</pre>", quote=True, reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^figlet_change:"))
async def figlet_handler(Client, query: CallbackQuery):
    try:
        # Extract the text from callback_data
        text = query.data.split(":", 1)[1]
        kul_text, keyboard = figle(text)
        await query.message.edit_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{kul_text}</pre>", reply_markup=keyboard)
    except Exception as e:
        await query.answer(f"Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}", show_alert=True)

__mod_name__ = "Fɪɢʟᴇᴛ" 
__help__="""
❍ /figlet*:* ᴍᴀᴋᴇs ғɪɢʟᴇᴛ ᴏғ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ
Example:\n\n`/figlet stark `"""