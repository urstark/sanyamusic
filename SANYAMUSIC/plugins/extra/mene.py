
from pyrogram import Client, filters
import requests
from SANYAMUSIC import app 

# Define a command handler for the /meme command
@app.on_message(filters.command("meme"))
async def meme_command(client, message):
    # API endpoint for random memes
    api_url = "https://meme-api.com/gimme"

    try:
        # Make a request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        # The API can return a list or a single object
        if "memes" in data and isinstance(data["memes"], list):
            meme_data = data["memes"][0]
        else:
            meme_data = data

        meme_url = meme_data.get("url")
        title = meme_data.get("title", "Meme")

        if not meme_url:
            await message.reply_text("sᴏʀʀʏ, I ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ ᴀ ᴍᴇᴍᴇ URL ɪɴ ᴛʜᴇ API ʀᴇsᴘᴏɴsᴇ.")
            return

        caption = f"**{title}**\n\nʀᴇǫᴜᴇsᴛ ʙʏ {message.from_user.mention}"

        # Send the meme image to the user with the modified caption
        await message.reply_photo(photo=meme_url, caption=caption)

    except requests.exceptions.RequestException as e:
        await message.reply_text(f"sᴏʀʀʏ, I ᴄᴏᴜʟᴅɴ'ᴛ ғᴇᴛᴄʜ ᴀ ᴍᴇᴍᴇ ᴀᴛ ᴛʜᴇ ᴍᴏᴍᴇɴᴛ. API ᴇʀʀᴏʀ: {e}")
    except (KeyError, IndexError) as e:
        await message.reply_text(f"sᴏʀʀʏ, I ᴄᴏᴜʟᴅɴ'ᴛ ᴘᴀʀsᴇ ᴛʜᴇ ᴍᴇᴍᴇ ᴅᴀᴛᴀ. ᴇʀʀᴏʀ: {e}")
