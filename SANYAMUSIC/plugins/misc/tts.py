
import asyncio
import os
from pyrogram import Client, filters
from gtts import gTTS
from SANYAMUSIC import app


def gtts_convert(text):
    """Synchronous function to perform gTTS conversion and save to file."""
    try:
        tts = gTTS(text=text, lang='hi')
        filepath = 'speech.mp3'
        tts.save(filepath)
        return filepath
    except Exception:
        print(f"gTTS error")
        return None

@app.on_message(filters.command('tts'))
async def text_to_speech(client, message):
    try:
        text = message.text.split(' ', 1)[1]
    except IndexError:
        await message.reply_text("Please provide text to convert to speech. Example: `/tts Hello`")
        return

    m = await message.reply_text("Converting text to speech...")
    
    # Run the blocking gTTS function in a separate thread
    speech_file = await asyncio.to_thread(gtts_convert, text)
    
    if speech_file and os.path.exists(speech_file):
        await client.send_audio(message.chat.id, speech_file, reply_to_message_id=message.id)
        os.remove(speech_file)
        await m.delete()
    else:
        await m.edit("Sorry, something went wrong while creating the speech file.")
