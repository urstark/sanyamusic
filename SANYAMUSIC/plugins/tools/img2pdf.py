
from io import BytesIO
from os import path, remove
from time import time
import img2pdf
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message

from SANYAMUSIC import app
from SANYAMUSIC.utils.errors import capture_err

from SANYAMUSIC.core.sections import section


async def convert(
    main_message: Message,
    reply_messages,
    status_message: Message,
    start_time: float,
):
    m = status_message

    documents = []

    for message in reply_messages:
        image = None
        if message.photo:
            image = message.photo
        elif message.document and message.document.mime_type.startswith("image"):
            image = message.document
        else:
            # Skip messages that are not photos or image documents
            continue

        if image.file_size > 5000000:
            await m.edit(f"sᴋɪᴘᴘɪɴɢ ᴀɴ ɪᴍᴀɢᴇ ʙᴇᴄᴀᴜsᴇ ɪᴛs sɪᴢᴇ ({image.file_size / 10**6:.2f}MB) ᴇxᴄᴇᴇᴅs ᴛʜᴇ 5MB ʟɪᴍɪᴛ.")
            continue

        documents.append(await message.download())

    if not documents:
        return await m.edit("ɴᴏ ᴠᴀʟɪᴅ ɪᴍᴀɢᴇs ғᴏᴜɴᴅ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ. Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴘʜᴏᴛᴏs ᴏʀ ɪᴍᴀɢᴇ ᴅᴏᴄᴜᴍᴇɴᴛs.")
    for img_path in documents:
        img = Image.open(img_path).convert("RGB")
        img.save(img_path, "JPEG", quality=100)

    pdf = BytesIO(img2pdf.convert(documents))
    pdf.name = "SANYA.pdf"

    if len(main_message.command) >= 2:
        names = main_message.text.split(None, 1)[1]
        if not names.endswith(".pdf"):
            pdf.name = names + ".pdf"
        else:
            pdf.name = names

    elapsed = round(time() - start_time, 2)

    await main_message.reply_document(
        document=pdf,
        caption=section(
            "IMG2PDF",
            body={
                "Title": pdf.name,
                "Size": f"{pdf.getbuffer().nbytes / (10 ** 6)}MB",
                "Pages": len(documents),
                "Took": f"{elapsed}s",
            },
        ),
    )

    await m.delete()
    pdf.close()
    for file in documents:
        if path.exists(file):
            remove(file)


@app.on_message(filters.command("pdf"))
@capture_err
async def img_to_pdf(_, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply(
            "Rᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ ᴀ ɢʀᴏᴜᴘ ᴏғ ɪᴍᴀɢᴇs ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛʜᴇᴍ ᴛᴏ PDF."
        )

    m = await message.reply_text("ᴄᴏɴᴠᴇʀᴛɪɴɢ..")
    start_time = time()

    if reply.media_group_id:
        messages = await app.get_media_group(
            message.chat.id,
            reply.id,
        )
        return await convert(message, messages, m, start_time)

    return await convert(message, [reply], m, start_time)