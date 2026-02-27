from SANYAMUSIC import app 
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant

spam_chats = []

# Gen-Z Aesthetic Lite Emojis
EMOJI = [
    "✨", "☁️", "🌈", "🦋", "🌸", "🌙", "🌊", "🍃", "💫", "⭐", 
    "🎨", "🍓", "🧊", "🧸", "🎈", "🎀", "🛸", "🍭", "🌻", "🍀",
    "⚡", "💎", "🍄", "🧁", "🐾", "🧿", "🐚", "🎋", "🎐", "🪐"
]

# Simple Fonts - Hindi Gen-Z Style Messages
TAGMES = [
    "Oye! Kahan ho sab? ✨",
    "Utho utho, group active hai! ☁️",
    "Online aao, thodi baatein karte hain! 🌈",
    "Khana khaya ki nahi? 🍓",
    "Umeed hai sab badhiya hoga! 💫",
    "Bohot time se dikhe nahi yahan! 🦋",
    "Kya scene hai? Online aao jaldi! ☕",
    "Good vibes only! 🧿",
    "Busy ho ya ignore kar rahe ho? 💀",
    "Group dry lag raha hai, VC join karo! 🌙",
    "Naya gaana baj raha hai! Sunne aao! 🎧",
    "Sabko yaad kar rahe hain hum... ✨",
    "Ghost member mat bano, reply karo! 👻",
    "Yo! Ek baar chat check karlo. ⚡",
    "Sab kushal mangal? 🌸",
    "Doston ko bhi bulao yahan! 🎈",
    "Chalo music bajate hain, aajaao! 🎵",
    "Bas aise hi check-in kar raha tha! Kaise ho? ⭐",
    "Group mein energy lao thodi! 🌊",
    "Chup-chup mat raho, kuch bolo! 🍃",
    "Aapko yaad kiya ja raha hai! 🛸",
    "Kaam kar rahe ho ya velle ho? 🧐",
    "Thodi der chill karte hain, aao! 🧸",
    "Paani peeyo aur online aao! 🧊",
    "Mast baatein chal rahi hain, join karo! 💎",
    "Bas 'Hi' bolne ke liye tag kiya! 🍭",
    "Aaj ka vibe ekdum sahi hai, aajaao! 🪐",
    "Koi baat karne ke liye free hai? 🌻",
    "Aapke messages miss kar rahe hain! 🎀",
    "No cap, group boring ho gaya hai bina tumhare! ⚡"
]

@app.on_message(filters.command(["tagall", "all", "tag", "mention"], prefixes=["/", "@", "#"]))
async def mentionall(client, message):
    chat_id = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply("Stupid ! i only tag in groups.")

    # Admin verification
    is_admin = False
    try:
        participant = await client.get_chat_member(chat_id, message.from_user.id)
        if participant.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            is_admin = True
    except UserNotParticipant:
        pass
        
    if not is_admin:
        return await message.reply("Heyyy ! this if only for admins.")

    # Mode detection: Replying to a message vs individual command
    if message.reply_to_message:
        mode = "text_on_reply"
        msg_to_tag = message.reply_to_message
    else:
        mode = "text_on_cmd"
        msg_to_tag = message

    if chat_id in spam_chats:
        return await message.reply("Heyyy ! Don't disturb me i'm tagging users. use /tagstop to stop me.")
    
    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""

    async for usr in client.get_chat_members(chat_id):
        if not chat_id in spam_chats:
            break
        if usr.user.is_bot:
            continue
        
        usrnum += 1
        usrtxt += f"[{usr.user.first_name}](tg://user?id={usr.user.id}) "

        # Ek message mein 5 logon ko tag karega taaki spam na lage
        if usrnum == 5:
            if mode == "text_on_cmd":
                # Standard tagging with random Hindi message
                txt = f"{usrtxt}\n\n{random.choice(TAGMES)}"
                await client.send_message(chat_id, txt)
            else:
                # Reply-based tagging with lite emojis
                await msg_to_tag.reply(f"{random.choice(EMOJI)} {usrtxt}")
            
            # 4 second ka delay taaki bot ban na ho ya lag na kare
            await asyncio.sleep(4)
            usrnum = 0
            usrtxt = ""

    try:
        spam_chats.remove(chat_id)
    except:
        pass

@app.on_message(filters.command(["tagoff", "tagstop", "stopall"]))
async def cancel_spam(client, message):
    if not message.chat.id in spam_chats:
        return await message.reply("I'm not tagging anyone currently.")
    
    is_admin = False
    try:
        participant = await client.get_chat_member(message.chat.id, message.from_user.id)
        if participant.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            is_admin = True
    except UserNotParticipant:
        pass

    if not is_admin:
        return await message.reply("Only admins can stop Tagging process.")
    
    try:
        spam_chats.remove(message.chat.id)
    except:
        pass
    return await message.reply(" Tagging stopped.")
