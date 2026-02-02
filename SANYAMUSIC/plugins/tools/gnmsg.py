
import re
from pyrogram import filters
import random
import asyncio
from SANYAMUSIC import app


# Using regex to make the trigger more robust and catch variations
@app.on_message(filters.regex(r"^(gn|good\s?night)$", flags=re.IGNORECASE))
async def goodnight_command_handler(client, message):
    sender = message.from_user.mention
    send_sticker = random.choice([True, False])
    if send_sticker:
        sticker_id = get_random_sticker()
        await client.send_sticker(message.chat.id, sticker_id, reply_to_message_id=message.id)
    else:
        emoji = get_random_emoji()
        await message.reply_text(f"**Gᴏᴏᴅ ɴɪɢʜᴛ, {sender}! Sʟᴇᴇᴘ ᴛɪɢʜᴛ. {emoji}**")
    await asyncio.sleep(3) # Small delay


def get_random_sticker():
    stickers = [
        "CAACAgUAAyEFAATKMLw9AAICFmkowc6ER7bQSjq3vR5B96N5gSGWAAJVCwAChAXgVycac263MmgrHgQ", # Sticker 1
        "CAACAgUAAyEFAATKMLw9AAICE2kowazL_zgPgwGsdkmZU9x-BYONAALhDAACFvnhVxeIzCaW-_SRHgQ", # Sticker 2
        "CAACAgUAAyEFAATKMLw9AAIByGkllwddFCcbbD4OnUdJJUZHO8nUAAJOEQACLJkAAVdYMT0-RxK89x4E", # Sticker 3
        "CAACAgUAAyEFAATKMLw9AAIBuWkllmatL6t7B0g5RTMEoYLJSWalAAKZFQACFB2QVZ_Rbw8ef2-HHgQ",
        "CAACAgQAAx0Ce9_hCAACaEVlwn7HeZhgwyVfKHc3WUGC_447IAACLgwAAkQwKVPtub8VAR018x4E",
    ]
    return random.choice(stickers)


def get_random_emoji():
    emojis = [
        "😴",
        "😪",
        "💤",
    ]
    return random.choice(emojis)
