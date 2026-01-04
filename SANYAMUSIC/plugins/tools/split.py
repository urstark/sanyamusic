
from pyrogram import Client, filters
from pyrogram.types import Message
import os

from SANYAMUSIC import app

@app.on_message(filters.command("split") & filters.reply)
async def split_file(client: Client, message: Message):
    replied_message = message.reply_to_message
    if not (replied_message and replied_message.document):
        await message.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴅᴏᴄᴜᴍᴇɴᴛ ғɪʟᴇ ᴛᴏ sᴘʟɪᴛ ɪᴛ.\n\n**ᴜsᴀɢᴇ:** `/split <number_of_lines>`")
        return

    if not replied_message.document.file_name.endswith(".txt"):
        await message.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ `.txt` ғɪʟᴇ.")
        return

    status_msg = await message.reply("ᴘʀᴏᴄᴇssɪɴɢ...")
    file_path = None
    try:
        try:
            num_lines = int(message.text.split(" ")[1])
        except (IndexError, ValueError):
            num_lines = 10  # Default number of lines

        await status_msg.edit("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ғɪʟᴇ...")
        file_path = await client.download_media(replied_message)

        if not os.path.exists(file_path):
            await status_msg.edit("ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ғɪʟᴇ.")
            return

        await status_msg.edit("sᴘʟɪᴛᴛɪɴɢ ғɪʟᴇ...")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
        except Exception as e:
            await status_msg.edit(f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ᴛʜᴇ ғɪʟᴇ: {e}")
            return

        if not lines:
            await status_msg.edit("Tʜᴇ ғɪʟᴇ ɪs ᴇᴍᴘᴛʏ.")
            return

        total_files = (len(lines) + num_lines - 1) // num_lines
        for i in range(0, len(lines), num_lines):
            part_num = i // num_lines + 1
            await status_msg.edit(f"sᴇɴᴅɪɴɢ ᴘᴀʀᴛ {part_num}/{total_files}...")
            split_lines = lines[i:i + num_lines]
            split_file_path = f"split_{part_num}.txt"
            try:
                with open(split_file_path, 'w', encoding='utf-8') as split_file:
                    split_file.writelines(split_lines)
                await client.send_document(chat_id=message.chat.id, document=split_file_path)
            except Exception as e:
                await message.reply(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴘᴀʀᴛ {part_num}: {e}")
                continue
            finally:
                if os.path.exists(split_file_path):
                    os.remove(split_file_path)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)