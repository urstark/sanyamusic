import asyncio
from pyrogram import Client, filters
import whois
from SANYAMUSIC import app

def get_domain_hosting_info(domain_name):
    try:
        domain_info = whois.whois(domain_name)
        return domain_info
    except whois.parser.PywhoisError as e:
        print(f"Error: {e}")
        return None


@app.on_message(filters.command("domain"))
async def get_domain_info(client, message):
    if len(message.command) > 1:
        domain_name = message.text.split(maxsplit=1)[1].strip()
        
        # Run the synchronous whois lookup in a separate thread
        try:
            domain_info = await asyncio.to_thread(get_domain_hosting_info, domain_name)
        except Exception as e:
            await message.reply(f"An error occurred: {e}")
            return

        if domain_info:
            response = (
                f"**ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ:** `{domain_info.domain_name}`\n"
                f"**ʀᴇsɪsᴛʀᴀʀ:** `{domain_info.registrar}`\n"
                f"**ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ:** `{domain_info.creation_date}`\n"
                f"**ᴇxᴘɪʀᴀᴛɪᴏɴ ᴅᴀᴛᴇ:** `{domain_info.expiration_date}`\n"
                f"**ɴᴀᴍᴇ sᴇʀᴠᴇʀs:**\n`" + '`\n`'.join(domain_info.name_servers or ['N/A']) + "`"
                # Add more details as needed
            )
        else:
            response = "Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴅᴏᴍᴀɪɴ ʜᴏsᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ."

        await message.reply(response)
    else:
        await message.reply("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ ᴀғᴛᴇʀ ᴛʜᴇ /domain ᴄᴏᴍᴍᴀɴᴅ.")
