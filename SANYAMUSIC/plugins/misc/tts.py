import asyncio
import os
import random
import edge_tts
from pyrogram import Client, filters
from SANYAMUSIC import app

# A list of realistic Indian female Neural voices
FEMALE_VOICES = [
    "hi-IN-SwaraNeural",  # Standard clear Hindi female
    "hi-IN-AnanyaNeural", # Soft/Cute Hindi female
    "en-IN-NeerjaNeural", # Indian English female (good for Hinglish)
    "en-IN-AnanyaNeural"  # Indian English female
]

@app.on_message(filters.command('tts'))
async def text_to_speech(client, message):
    try:
        # Check if the user is replying to a message or providing text
        if message.reply_to_message and not len(message.command) > 1:
            text = message.reply_to_message.text or message.reply_to_message.caption
        else:
            text = message.text.split(' ', 1)[1]
    except (IndexError, AttributeError):
        await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.\n\n**Usage:** `/tts [text]`")
        return

    if not text:
        return await message.reply_text("I ᴄᴀɴ'ᴛ ᴄᴏɴᴠᴇʀᴛ ᴇᴍᴘᴛʏ ᴛᴇxᴛ!")

    m = await message.reply_text("✨ **Gᴇɴᴇʀᴀᴛɪɴɢ Rᴀɴᴅᴏᴍ Cᴜᴛᴇ Vᴏɪᴄᴇ...**")
    filepath = 'speech.mp3'

    # Randomly pick one of the female voices for this specific request
    selected_voice = random.choice(FEMALE_VOICES)

    try:
        # Generate the audio using edge-tts (natively async)
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(filepath)

        if os.path.exists(filepath):
            # Send the audio file to the chat
            await client.send_audio(
                message.chat.id, 
                filepath, 
                reply_to_message_id=message.id,
                title=f"Voice: {selected_voice.split('-')[2]}",
                performer="Edge-TTS"
            )
            # Cleanup local files
            os.remove(filepath)
            await m.delete()
        else:
            await m.edit("Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛʜᴇ sᴘᴇᴇᴄʜ ғɪʟᴇ.")
            
    except Exception as e:
        print(f"TTS Error: {e}")
        await m.edit("Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴄʀᴇᴀᴛɪɴɢ ᴛʜᴇ ᴠᴏɪᴄᴇ.")
        if os.path.exists(filepath):
            os.remove(filepath)
