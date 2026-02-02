import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pydub import AudioSegment
import speech_recognition as sr
from SANYAMUSIC import app
# --------------------------------------
# Note: The following function is synchronous and CPU-intensive.
# For a production bot, it's better to run this in a separate thread
# to avoid blocking the event loop.
def convert_video_to_text(video_path):
    audio = AudioSegment.from_file(video_path)
    audio.export("audio.wav", format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    finally:
        os.remove("audio.wav")

@app.on_message(filters.command("vtxt") & filters.reply)
async def convert_video_to_text_cmd(_, message: Message):
    replied_message = message.reply_to_message
    if not replied_message.video:
        await message.reply_text("Please reply to a video message to use this command.")
        return

    video_path = None
    try:
        processing_msg = await message.reply_text("Processing video...")
        video_path = await replied_message.download("video.mp4")
        
        text_result = await asyncio.to_thread(convert_video_to_text, video_path)

        with open("file.txt", "w", encoding="utf-8") as file:
            file.write(text_result)
        
        await message.reply_document("file.txt")
        await processing_msg.delete()

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists("file.txt"):
            os.remove("file.txt")

@app.on_message(filters.command("remove", prefixes="/") & filters.reply)
async def remove_media(client, message: Message):
    replied_message = message.reply_to_message

    if not replied_message or not replied_message.video:
        await message.reply_text("The replied message is not a video.")
        return

    if len(message.command) < 2:
        await message.reply_text("Please specify what to remove. Use `/remove audio` or `/remove video`.")
        return

    command = message.command[1].lower()
    file_path = None
    output_path = None
    try:
        processing_msg = await message.reply_text("Processing...")
        file_path = await app.download_media(replied_message.video)

        if command == "audio":
            output_path = "output.mp4"
            proc = await asyncio.create_subprocess_shell(f"ffmpeg -i {file_path} -c copy -an {output_path}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            await app.send_video(message.chat.id, output_path, caption="Video without audio")
        elif command == "video":
            output_path = "output.mp3"
            await asyncio.to_thread(AudioSegment.from_file(file_path).export, output_path, format="mp3")
            await app.send_audio(message.chat.id, output_path, caption="Audio from video")
        else:
            await message.reply_text("Invalid command. Please use either `/remove audio` or `/remove video`.")
        await processing_msg.delete()
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
