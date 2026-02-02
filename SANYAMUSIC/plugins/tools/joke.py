
import httpx
from SANYAMUSIC import app
from pyrogram import Client, filters

# Using a new, more reliable API for Hindi jokes
JOKE_API_ENDPOINT = "https://v2.jokeapi.dev/joke/Any"

@app.on_message(filters.command("joke"))
async def joke(_, message):
    try:
        async with httpx.AsyncClient() as client:
            # Exclude some categories to keep it SFW
            params = {"blacklistFlags": "nsfw,religious,political,racist,sexist,explicit"}
            response = await client.get(JOKE_API_ENDPOINT, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        category = data.get("category", "N/A")

        if data.get("type") == "single":
            joke_text = data["joke"]
        elif data.get("type") == "twopart":
            joke_text = f"{data['setup']}\n\n{data['delivery']}"
        else:
            await message.reply_text("Sᴏʀʀʏ, I ʀᴇᴄᴇɪᴠᴇᴅ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴊᴏᴋᴇ ғᴏʀᴍᴀᴛ ғʀᴏᴍ ᴛʜᴇ API.")
            return
        
        final_message = f"**Category:** `{category}`\n\n{joke_text}"
        await message.reply_text(final_message)

    except httpx.HTTPStatusError as e:
        await message.reply_text(f"Sᴏʀʀʏ, ᴛʜᴇ ᴊᴏᴋᴇ API ʀᴇᴛᴜʀɴᴇᴅ ᴀɴ ᴇʀʀᴏʀ: {e.response.status_code}")
    except Exception as e:
        await message.reply_text(f"Sᴏʀʀʏ, I ᴄᴏᴜʟᴅɴ'ᴛ ғᴇᴛᴄʜ ᴀ ᴊᴏᴋᴇ ᴀᴛ ᴛʜᴇ ᴍᴏᴍᴇɴᴛ. Eʀʀᴏʀ: {e}")
