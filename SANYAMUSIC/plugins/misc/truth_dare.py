from pyrogram import Client, filters
import aiohttp
from SANYAMUSIC import app

# Truth or Dare API URLs
truth_api_url = "https://api.truthordarebot.xyz/v1/truth"
dare_api_url = "https://api.truthordarebot.xyz/v1/dare"

@app.on_message(filters.command("truth"))
async def get_truth(client, message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(truth_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    truth_question = data.get("question")
                    await message.reply_text(f"Truth question:\n\n{truth_question}")
                else:
                    await message.reply_text("Failed to fetch a truth question. Please try again later.")
            
    except Exception as e:
        print(f"Error: {e}") # Print error to console for debugging
        # FIXED: Added 'await' here
        await message.reply_text("An error occurred while fetching a truth question.")

@app.on_message(filters.command("dare"))
async def get_dare(client, message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(dare_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    dare_question = data.get("question")
                    await message.reply_text(f"Dare question:\n\n{dare_question}")
                else:
                    await message.reply_text("Failed to fetch a dare question. Please try again later.")
            
    except Exception as e:
        print(f"Error: {e}")
        # FIXED: Added 'await' here
        await message.reply_text("An error occurred while fetching a dare question.")
