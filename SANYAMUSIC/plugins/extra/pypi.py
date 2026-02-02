
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from SANYAMUSIC import app


@app.on_message(filters.command("pypi", prefixes="/"))
async def pypi_command(client, message):
    try:
        package_name = message.command[1]
    except IndexError:
        await message.reply("Please provide a package name after the /pypi command.")
        return

    api_url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        response = requests.get(api_url)
        # Check if the package was found
        if response.status_code == 404:
            await message.reply(f"Package `{package_name}` not found on PyPI.")
            return
        
        # Raise an exception for other bad status codes
        response.raise_for_status()
        
        pypi_info = response.json().get("info", {})
        
        # Creating a message with PyPI information
        info_message = (
            f"**Package:** `{pypi_info.get('name', 'N/A')}`\n"
            f"**Version:** `{pypi_info.get('version', 'N/A')}`\n"
            f"**Summary:** `{pypi_info.get('summary', 'N/A')}`"
        )
        
        homepage = pypi_info.get("project_urls", {}).get("Homepage")
        pypi_url = pypi_info.get("package_url")
        
        buttons = []
        if homepage:
            buttons.append([InlineKeyboardButton("Homepage", url=homepage)])
        if pypi_url:
            buttons.append([InlineKeyboardButton("PyPI Page", url=pypi_url)])

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await message.reply(info_message, reply_markup=reply_markup, disable_web_page_preview=True)

    except requests.exceptions.RequestException as e:
        await message.reply(f"An error occurred while fetching information from PyPI: {e}")
