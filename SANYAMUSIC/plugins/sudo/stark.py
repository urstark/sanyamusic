import requests
import random
from SANYAMUSIC import app, userbot
from SANYAMUSIC.misc import SUDOERS
from pyrogram import * 
from pyrogram.types import *
from SANYAMUSIC.utils.Sanya_ban import admin_filter


stark_text = [
"hey please don't disturb me.",
"who are you",    
"aap kon ho",
"aap mere owner to nhi lgte ",
"hey tum mera name kyu le rhe ho meko sone do",
"ha bolo kya kaam hai ",
"dekho abhi mai busy hu ",
"hey i am busy",
"aapko smj nhi aata kya ",
"leave me alone",
"dude what happend",    
]

strict_txt = [
"i can't restrict against my besties",
"are you serious i am not restrict to my friends",
"hey stupid admin ", 
"ha ye phele krlo maar lo ek dusre ko",  
"i can't, he is my closest friend",
"i love him please don't restict this user try to understand "
]


 
ban = ["ban","boom"]
unban = ["unban",]
mute = ["mute","silent","shut"]
unmute = ["unmute","speak","free"]
kick = ["kick", "out","nikaal","nikal"]
promote = ["promote","adminship"]
fullpromote = ["fullpromote","fulladmin"]
demote = ["demote","lelo"]
group = ["group"]
channel = ["channel"]



# ========================================= #


@app.on_message(filters.command(["stark", "sanya", "baby"], prefixes=["/", "!", ""]) & admin_filter)
async def restriction_app(client, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply(random.choice(stark_text))
    data = [x.lower() for x in message.command[1:]]
    
    if reply:
        user_id = reply.from_user.id
        for banned in data:
            print(f"present {banned}")
            if banned in ban:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))          
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await message.reply("Dᴏɴᴇ!, ɪ ʙᴀɴɴᴇᴅ ᴛʜᴇ ᴜsᴇʀ")
                    
        for unbanned in data:
            print(f"present {unbanned}")
            if unbanned in unban:
                await client.unban_chat_member(chat_id, user_id)
                await message.reply(f"Sᴜʀᴇ, ᴀs ʏᴏᴜʀ ᴡɪsʜ. ᴜsᴇʀ ᴜɴʙᴀɴɴᴇᴅ!") 
                
        for kicked in data:
            print(f"present {kicked}")
            if kicked in kick:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))
                
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await client.unban_chat_member(chat_id, user_id)
                    await message.reply("Gᴏᴛ ɪᴛ, ᴜsᴇʀ ᴋɪᴄᴋᴇᴅ!") 
                    
        for muted in data:
            print(f"present {muted}") 
            if muted in mute:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))
                
                else:
                    permissions = ChatPermissions(can_send_messages=False)
                    await message.chat.restrict_member(user_id, permissions)
                    await message.reply(f"Mᴜᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!, ᴜғғ ᴅɪsɢᴜsᴛɪɴɢ ᴘᴇᴏᴘʟᴇ.") 
                    
        for unmuted in data:
            print(f"present {unmuted}")            
            if unmuted in unmute:
                permissions = ChatPermissions(can_send_messages=True)
                await message.chat.restrict_member(user_id, permissions)
                await message.reply(f"Hᴜʜ, OK sɪʀ! Usᴇʀ ᴜɴᴍᴜᴛᴇᴅ.")   


        for promoted in data:
            print(f"present {promoted}")            
            if promoted in promote:
                await client.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=False,
                    can_pin_messages=True,
                    can_promote_members=False,
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                       )
                     )
                await message.reply("ᴘʀᴏᴍᴏᴛᴇᴅ! ᴜsᴇʀ ɪs ɴᴏᴡ ᴀᴅᴍɪɴ")

        for demoted in data:
            print(f"present {demoted}")            
            if demoted in demote:
                await client.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                       )
                     )
                await message.reply("ᴅᴇᴍᴏᴛᴇᴅ !")


        for fullpromoted in data:
            print(f"present {fullpromoted}")            
            if fullpromoted in fullpromote:
                await client.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=True,
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                   )
                 )
                await message.reply("sᴜʀᴇ, ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ғᴜʟʟᴘʀᴏᴍᴏᴛᴇᴅ! ᴡɪᴛʜ ᴀʟʟ ʀɪɢʜᴛs.")
