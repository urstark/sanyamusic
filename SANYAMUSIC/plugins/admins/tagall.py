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
        return await message.reply("Stupid! I only tag in groups.")

    # Admin verification
    is_admin = False
    try:
        participant = await client.get_chat_member(chat_id, message.from_user.id)
        if participant.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            is_admin = True
    except Exception:
        pass
        
    if not is_admin:
        return await message.reply("Heyyy! This is only for admins.")

    if chat_id in spam_chats:
        return await message.reply("Don't disturb me, I'm already tagging users. Use /tagstop to stop.")
    
    spam_chats.append(chat_id)
    
    # Mode detection
    is_reply = True if message.reply_to_message else False
    usrnum = 0
    usrtxt = ""

    async for usr in client.get_chat_members(chat_id):
        # Stop if the command /tagstop was used
        if chat_id not in spam_chats:
            break
        
        # Skip bots
        if usr.user.is_bot:
            continue
        
        # --- MODE 1: ONE BY ONE (No Reply) ---
        if not is_reply:
            tag_link = f"[{usr.user.first_name}](tg://user?id={usr.user.id})"
            # Send unique message for every member
            await client.send_message(chat_id, f"{tag_link} {random.choice(TAGMES)}")
            # 3 second delay for individual tags to avoid flood
            await asyncio.sleep(3)

        # --- MODE 2: BATCH TAGGING (On Reply) ---
        else:
            usrnum += 1
            usrtxt += f"[{usr.user.first_name}](tg://user?id={usr.user.id}) "

            # Tag 5 members per message as a reply to the original target
            if usrnum == 5:
                await message.reply_to_message.reply(f"{random.choice(EMOJI)} {usrtxt}")
                await asyncio.sleep(4) # 4 second delay for batch tags
                usrnum = 0
                usrtxt = ""

    # Catch any remaining users for the Reply Mode
    if is_reply and usrtxt:
        await message.reply_to_message.reply(f"{random.choice(EMOJI)} {usrtxt}")

    try:
        spam_chats.remove(chat_id)
    except:
        pass

@app.on_message(filters.command(["tagoff", "tagstop", "stopall"]))
async def cancel_spam(client, message):
    if not message.chat.id in spam_chats:
        return await message.reply("I'm not tagging anyone currently.")
    
    # Admin verification for stopping
    is_admin = False
    try:
        participant = await client.get_chat_member(message.chat.id, message.from_user.id)
        if participant.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            is_admin = True
    except Exception:
        pass

    if not is_admin:
        return await message.reply("Only admins can stop the tagging process.")
    
    if message.chat.id in spam_chats:
        spam_chats.remove(message.chat.id)
        return await message.reply("Tagging process stopped.")
