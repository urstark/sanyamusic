
from pyrogram import Client, filters
from SANYAMUSIC import app
from config import BOT_USERNAME


def hex_to_text(hex_string):
    try:
        text = bytes.fromhex(hex_string).decode('utf-8')
        return text
    except Exception as e:
        return f"Error decoding hex: {str(e)}"


def text_to_hex(text):
    hex_representation = ' '.join(format(ord(char), 'x') for char in text)
    return hex_representation


@app.on_message(filters.command("code"))
async def convert_text(_, message):
    if len(message.command) > 1:
        input_text = " ".join(message.command[1:])

        # Try to decode if it looks like hex, otherwise encode
        try:
            # Attempt to decode from hex
            decoded_text = hex_to_text(input_text.replace(" ", ""))
            response_text = (
                f"**Hex to Text**\n\n"
                f"**Input Hex:**\n`{input_text}`\n\n"
                f"**Decoded Text:**\n`{decoded_text}`\n\n"
                f"**BY:** @{BOT_USERNAME}"
            )
        except ValueError:
            # If decoding fails, encode to hex
            hex_representation = text_to_hex(input_text)
            response_text = f"**Text to Hex**\n\n**Input Text:**\n`{input_text}`\n\n**Hex Representation:**\n`{hex_representation}`\n\n**BY:** @{BOT_USERNAME}"

        await message.reply_text(response_text)
    else:
        await message.reply_text("Please provide text to encode or hex to decode after the `/code` command.")
