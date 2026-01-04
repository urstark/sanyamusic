from pyrogram import Client, filters
import requests
from SANYAMUSIC import app

# Truth or Dare API URLs
truth_api_url = "https://api.truthordarebot.xyz/v1/truth"
dare_api_url = "https://api.truthordarebot.xyz/v1/dare"

@app.on_message(filters.command("truth"))
async def get_truth(client, message):
    try:
        # Make a GET request to the Truth API
        # Note: 'requests' is blocking, but for simple text bots this works fine.
        response = requests.get(truth_api_url)
        
        if response.status_code == 200:
            # Based on your screenshot, the key "question" is correct
            truth_question = response.json().get("question")
            
            # FIXED: Added 'await' here
            await message.reply_text(f"Truth question:\n\n{truth_question}")
        else:
            # FIXED: Added 'await' here
            await message.reply_text("Failed to fetch a truth question. Please try again later.")
            
    except Exception as e:
        print(f"Error: {e}") # Print error to console for debugging
        # FIXED: Added 'await' here
        await message.reply_text("An error occurred while fetching a truth question.")

@app.on_message(filters.command("dare"))
async def get_dare(client, message):
    try:
        # Make a GET request to the Dare API
        response = requests.get(dare_api_url)
        
        if response.status_code == 200:
            dare_question = response.json().get("question")
            
            # FIXED: Added 'await' here
            await message.reply_text(f"Dare question:\n\n{dare_question}")
        else:
            # FIXED: Added 'await' here
            await message.reply_text("Failed to fetch a dare question. Please try again later.")
            
    except Exception as e:
        print(f"Error: {e}")
        # FIXED: Added 'await' here
        await message.reply_text("An error occurred while fetching a dare question.")
