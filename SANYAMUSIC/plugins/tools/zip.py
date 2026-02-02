
from pyrogram import Client, filters
import os
import shutil
import zipfile
from SANYAMUSIC import app


def zip_file(file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(file_path, os.path.basename(file_path))


def unzip_file(zip_file_path, output_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        zip_file.extractall(output_folder)


@app.on_message(filters.command("zip"))
async def zip_command(client, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.reply_text("Rᴇᴘʟʏ ᴛᴏ ᴀ ғɪʟᴇ ᴡɪᴛʜ /ᴢɪᴘ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ ᴢɪᴘ ғɪʟᴇ.")
        return

    status_message = await message.reply_text("Zɪᴘᴘɪɴɢ...")
    original_file = None
    zip_file_path = None
    try:
        original_file = await client.download_media(message.reply_to_message)
        if original_file:
            zip_file_path = f"{original_file}.zip"
            zip_file(original_file, zip_file_path)

            await message.reply_document(zip_file_path)
            await status_message.delete()
        else:
            await status_message.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ғɪʟᴇ.")
    except Exception as e:
        await status_message.edit(f"Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")
    finally:
        if original_file and os.path.exists(original_file):
            os.remove(original_file)
        if zip_file_path and os.path.exists(zip_file_path):
            os.remove(zip_file_path)


@app.on_message(filters.command("unzip"))
async def unzip_command(client, message):
    if not (message.reply_to_message and message.reply_to_message.document and message.reply_to_message.document.file_name.endswith(".zip")):
        await message.reply_text("Rᴇᴘʟʏ ᴛᴏ ᴀ ᴢɪᴘ ғɪʟᴇ ᴡɪᴛʜ /ᴜɴᴢɪᴘ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ɪᴛs ᴄᴏɴᴛᴇɴᴛs.")
        return

    status_message = await message.reply_text("Uɴᴢɪᴘᴘɪɴɢ...")
    zip_file_path = None
    output_folder = None
    try:
        zip_file_path = await client.download_media(message.reply_to_message)
        if zip_file_path:
            output_folder = f"{zip_file_path}_unzipped"
            os.makedirs(output_folder, exist_ok=True)
            unzip_file(zip_file_path, output_folder)

            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    await message.reply_document(file_path)
            await status_message.delete()
        else:
            await status_message.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ᴢɪᴘ ғɪʟᴇ.")
    except Exception as e:
        await status_message.edit(f"Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")
    finally:
        if zip_file_path and os.path.exists(zip_file_path):
            os.remove(zip_file_path)
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder)
