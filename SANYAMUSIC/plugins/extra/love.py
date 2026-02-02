
from pyrogram import Client, filters
import random
from SANYAMUSIC import app

def get_random_message(love_percentage):
    if love_percentage <= 30:
        return random.choice([
            "Love is in the air but needs a little spark.",
            "A good start but there's room to grow.",
            "It's just the beginning of something beautiful."
        ])
    elif love_percentage <= 70:
        return random.choice([
            "A strong connection is there. Keep nurturing it.",
            "You've got a good chance. Work on it.",
            "Love is blossoming, keep going."
        ])
    else:
        return random.choice([
            "Wow! It's a match made in heaven!",
            "Perfect match! Cherish this bond.",
            "Destined to be together. Congratulations!"
        ])
        
@app.on_message(filters.command("love", prefixes="/"))
async def love_command(client, message):
    # Using message.command is more robust for parsing arguments
    if len(message.command) >= 3:
        name1 = message.command[1]
        name2 = message.command[2]
        
        love_percentage = random.randint(40, 100)
        love_message = get_random_message(love_percentage)

        response = f"**﹝⌬﹞ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛɪᴏɴ**\n\n`{name1}` 💕 + `{name2}` 💕 = **{love_percentage}%**\n\n{love_message}"
        await message.reply_text(response)
    else:
        await message.reply_text("Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛᴡᴏ ɴᴀᴍᴇs ᴀғᴛᴇʀ ᴛʜᴇ /love ᴄᴏᴍᴍᴀɴᴅ.\n\n**ᴜsᴀɢᴇ:** `/love [name1] [name2]`")
