
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from SANYAMUSIC import app


def check_proxy(proxy):
    url = "https://api.ipify.org?format=json"
    proxies = {
        "http": f"http://{proxy}",
        "https": f"https://{proxy}",
    }
    
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            return "Live ✅"
        else:
            return "Dead ❌"
    except requests.RequestException:
        return "Dead ❌"


@app.on_message(filters.command("proxy"))
async def single_proxy_handler(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply("ᴜsᴀɢᴇ: /proxy <single_proxy>")
        return
    
    proxy = message.command[1]
    result = check_proxy(proxy)
    response = f"""
┏━━━━━━━⍟
┃𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿
┗━━━━━━━━━━━⊛

{proxy}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {result}

⌥ 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {message.from_user.first_name}
"""
    await message.reply(response)


@app.on_message(filters.command("proxytxt"))
async def proxytxt_handler(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ .ᴛxᴛ ғɪʟᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴘʀᴏxɪᴇs ᴡɪᴛʜ ᴛʜᴇ /proxytxt ᴄᴏᴍᴍᴀɴᴅ.")
        return
    
    file_id = message.reply_to_message.document.file_id
    file_path = await client.download_media(file_id)
    
    with open(file_path, 'r') as file:
        proxies = file.readlines()
    
    total_proxies = len(proxies)
    live_proxies = 0
    dead_proxies = 0
    
    live_proxy_list = []
    results = []
    
    summary_message = await message.reply(f"""
┏━━━━━━━⍟
┃𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗦𝘂𝗺𝗺𝗮𝗿𝘆
┗━━━━━━━━━━━⊛

𝗧𝗼𝘁𝗮𝗹 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {total_proxies}
𝗟𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {live_proxies}
𝗗𝗲𝗮𝗱 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {dead_proxies}
""")
    
    for proxy in proxies:
        proxy = proxy.strip()
        result = check_proxy(proxy)
        if result == "Live ✅":
            live_proxies += 1
            live_proxy_list.append(proxy)
        else:
            dead_proxies += 1
        results.append(f"{proxy} - {result}")
        
        await summary_message.edit_text(f"""
┏━━━━━━━⍟
┃𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗦𝘂𝗺𝗺𝗮𝗿𝘆
┗━━━━━━━━━━━⊛

𝗧𝗼𝘁𝗮𝗹 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {total_proxies}
𝗟𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {live_proxies}
𝗗𝗲𝗮𝗱 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {dead_proxies}
""")
    
    if live_proxy_list:
        with open("live_proxies.txt", 'w') as live_file:
            live_file.write("\n".join(live_proxy_list))
        await message.reply_document(document="live_proxies.txt", filename="live_proxies.txt")
    
    await summary_message.edit_text(f"""
┏━━━━━━━⍟
┃𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗦𝘂𝗺𝗺𝗮𝗿𝘆
┗━━━━━━━━━━━⊛

𝗧𝗼𝘁𝗮𝗹 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {total_proxies}
𝗟𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {live_proxies}
𝗗𝗲𝗮𝗱 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: {dead_proxies}
""")