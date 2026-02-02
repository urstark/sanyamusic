
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from SANYAMUSIC import app


@app.on_message(filters.command("population"))
async def country_command_handler(client: Client, message: Message):
    try:
        # Extract the country code from the command
        country_code = message.command[1]
    except IndexError:
        await message.reply_text("Please provide a country code. Usage: `/population US`")
        return

    # Call the external API for country information
    api_url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    
    try:
        response = requests.get(api_url)

        if response.status_code == 404:
            await message.reply_text(f"Invalid country code: `{country_code}`. Please use a valid ISO 3166-1 alpha-2 or alpha-3 code.")
            return

        response.raise_for_status()  # Raise an HTTPError for bad responses

        country_data = response.json()
        if country_data:
            country_info = country_data[0]
            # Extract relevant information from the API response
            country_name = country_info.get("name", {}).get("common", "N/A")
            capital_list = country_info.get("capital", [])
            capital = capital_list[0] if capital_list else "N/A"
            population = country_info.get("population", "N/A")

            response_text = (
                f"**Country Information for {country_name}**\n\n"
                f"**Name:** `{country_name}`\n"
                f"**Capital:** `{capital}`\n"
                f"**Population:** `{population:,}`"
            )
        else:
            response_text = "Could not parse country information from the API response."
    except requests.exceptions.HTTPError as http_err:
        response_text = f"An HTTP error occurred: `{http_err}`"
    except Exception as err:
        response_text = f"An unexpected error occurred: `{err}`"

    # Send the response to the Telegram chat
    await message.reply_text(response_text)