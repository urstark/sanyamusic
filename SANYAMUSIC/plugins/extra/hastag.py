
import httpx
from bs4 import BeautifulSoup as  BSP
from SANYAMUSIC import app as SANYA
from pyrogram import filters

url = "https://all-hashtag.com/library/contents/ajax_generator.php"

@SANYA.on_message(filters.command("hastag"))
async def hastag(bot, message):
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("Example:\n\n/hastag python")

    data = {"keyword": text, "filter": "top"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            response.raise_for_status()

        content = BSP(response.text, 'html.parser').find("div", {"class":"copy-hashtags"})
        if content:
            await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ  ʜᴀsᴛᴀɢ :\n<pre>{content.string}</pre>", quote=True)
        else:
            await message.reply_text("ᴄᴏᴜʟᴅ ɴᴏᴛ ғɪɴᴅ ᴀɴʏ ʜᴀsʜᴛᴀɢs ғᴏʀ ᴛʜᴀᴛ ᴋᴇʏᴡᴏʀᴅ.")
    except httpx.HTTPError as e:
        await message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ʜᴀsʜᴛᴀɢs: {e}")
    
mod_name = "Hᴀsʜᴛᴀɢ"
help= """
Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʜᴀsʜᴛᴀɢ ɢᴇɴᴇʀᴀᴛᴏʀ ᴡʜɪᴄʜ ᴡɪʟʟ ɢɪᴠᴇ ʏᴏᴜ ᴛʜᴇ ᴛᴏᴘ 𝟹𝟶 ᴀɴᴅ ᴍᴏʀᴇ ʜᴀsʜᴛᴀɢs ʙᴀsᴇᴅ ᴏғғ ᴏғ ᴏɴᴇ ᴋᴇʏᴡᴏʀᴅ sᴇʟᴇᴄᴛɪᴏɴ.
° /hastag enter word to generate hastag.
°Exᴀᴍᴘʟᴇ:  /hastag python """
