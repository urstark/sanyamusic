
from pyrogram import Client, filters
from pyrogram.types import Message
import qrcode
from SANYAMUSIC import app
from PIL import Image
import io


# Function to create a QR code
def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code to a bytes object to send with Pyrogram
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)  # Go to the start of the bytes object

    return img_bytes


@app.on_message(filters.command("qr"))
async def qr_handler(client, message: Message):
    # Using message.text to get the arguments
    if message.reply_to_message:
        input_text = message.reply_to_message.text
    else:
        input_text = " ".join(message.command[1:])

    if input_text:
        qr_image = generate_qr_code(input_text)
        await message.reply_photo(qr_image, caption=f"**ɢᴇɴᴇʀᴀᴛᴇᴅ QR ғᴏʀ:**\n`{input_text}`")
    else:
        await message.reply_text("Please provide the text for the QR code after the command. Example usage: /qr text")
