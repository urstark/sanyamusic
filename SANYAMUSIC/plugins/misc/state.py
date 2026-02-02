
import asyncio
from pyrogram import Client, filters
import pycountry
from SANYAMUSIC import app 

def find_states_sync(country_name):
    """Synchronous function to find states for a given country."""
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            return f"I couldn't find the country '{country_name}'. Please make sure it's spelled correctly."

        subdivisions = list(pycountry.subdivisions.get(country_code=country.alpha_2))
        if not subdivisions:
            return f"No states/subdivisions found for {country_name}."

        states_list = [state.name for state in subdivisions]
        return f"**States of {country_name}:**\n" + "\n".join(states_list)
    except Exception:
        return f"I couldn't find the country '{country_name}'. Please make sure it's spelled correctly."

@app.on_message(filters.command("get_states"))
async def get_states(client, message):
    try:
        country_name = message.text.split(' ', 1)[1]
    except IndexError:
        await message.reply_text("Please provide a country name. Example:\n`/get_states Canada`")
        return

    # Run the blocking pycountry lookup in a separate thread
    states_message = await asyncio.to_thread(find_states_sync, country_name)

    await message.reply_text(states_message)
