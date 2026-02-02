
from pyrogram import Client, filters
from SANYAMUSIC import app
import requests
import asyncio


@app.on_message(filters.command("weather"))
async def weather(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("Please provide a location. For example: `/weather New York`")
            return

        location = " ".join(message.command[1:])
        weather_url = f"https://wttr.in/{location}.png"
        
        # Run the blocking 'requests' call in a separate thread
        response = await asyncio.to_thread(requests.get, weather_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Reply with the weather information as a photo
        await message.reply_photo(photo=response.content, caption=f"**Here's the weather for:** `{location}`")

    except requests.exceptions.HTTPError as e:
        await message.reply_text(f"Could not get weather for the specified location. Error: {e}")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
