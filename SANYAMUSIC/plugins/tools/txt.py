
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from SANYAMUSIC import app

# Function to save the message text to a .txt file
def save_message_to_txt(message_text: str, filename: str = "messages.txt"):
    with open(filename, "a") as f:
        f.write(message_text + "\n")

@app.on_message(filters.command("txt"))
async def save_replied_message(client: Client, message: Message):
    replied_message = message.reply_to_message
    if not replied_message:
        await message.reply_text("Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀs ᴀ .ᴛxᴛ ғɪʟᴇ.\n\n**Usᴀɢᴇ:** Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴛʏᴘᴇ /txt")
        return

    if replied_message.text:
        save_message_to_txt(replied_message.text)
        
        # Extract the name of the person who generated the file
        sender_name = message.from_user.first_name
        if message.from_user.last_name:
            sender_name += f" {message.from_user.last_name}"
        
        # Create the caption with the sender's name
        caption = (
            "┏━━━━━━━⍟\n"
            "┃ 𝗛𝗲𝗿𝗲 𝗶𝘀 𝘆𝗼𝘂𝗿 .𝘁𝘅𝘁 𝗳𝗶𝗹𝗲 ✅\n"
            "┗━━━━━━━━━━━━━━━⊛\n"
            f"⊙ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐛𝐲 :- {sender_name}"
        )
        
        # Send the messages.txt file to the user with the specified caption
        if os.path.exists("messages.txt"):
            await message.reply_document("messages.txt", caption=caption)
        
        # Delete the messages.txt file after sending it
        os.remove("messages.txt")
    else:
        await message.reply_text("Tʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴏᴇs ɴᴏᴛ ᴄᴏɴᴛᴀɪɴ ᴀɴʏ ᴛᴇxᴛ ᴛᴏ sᴀᴠᴇ.")
        