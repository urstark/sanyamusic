
from pyrogram import filters
from pyrogram.types import Message

from SANYAMUSIC import app
from SANYAMUSIC.core.call import SANYA

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await SANYA.stop_stream_force(message.chat.id)
