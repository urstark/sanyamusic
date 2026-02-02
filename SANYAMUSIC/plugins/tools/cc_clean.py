
from pyrogram import Client, filters
import re
from io import BytesIO
from SANYAMUSIC import app

def filter_bin(input_text):
    pattern = r'\d{15,16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    matches = re.findall(pattern, input_text)
    return '\n'.join(matches)

@app.on_message(filters.command("clean") & filters.reply)
async def clean_command(client, message):
    replied_message = message.reply_to_message
    text_to_process = ""

    if replied_message.text:
        text_to_process = replied_message.text
    elif replied_message.document:
        doc = replied_message.document
        if doc.file_name and doc.file_name.endswith('.txt'):
            try:
                file_path = await client.download_media(doc)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    text_to_process = file.read()
            except Exception as e:
                await message.reply(f"ᴇʀʀᴏʀ ʀᴇᴀᴅɪɴɢ ғɪʟᴇ: {e}")
                return
        else:
            await message.reply("Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ .txt ᴅᴏᴄᴜᴍᴇɴᴛ ᴏʀ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ.")
            return
    else:
        await message.reply("Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ ᴀ ᴅᴏᴄᴜᴍᴇɴᴛ.")
        return

    filtered_text = filter_bin(text_to_process)

    if not filtered_text:
        await message.reply("ɴᴏ ᴍᴀᴛᴄʜɪɴɢ ᴅᴀᴛᴀ ғᴏᴜɴᴅ.")
    else:
        output = BytesIO()
        output.write(filtered_text.encode('utf-8'))
        output.name = "cc_clean.txt"
        await client.send_document(
            chat_id=message.chat.id,
            document=output,
            caption="Hᴇʀᴇ ɪs ᴛʜᴇ Cʟᴇᴀɴ 🫧 🪥 CC 💳 Rᴇsᴜʟᴛ",
            reply_to_message_id=message.id
        )