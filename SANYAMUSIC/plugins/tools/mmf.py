import asyncio
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from SANYAMUSIC import app

@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("**Reply to a photo or sticker after the /mmf command.**")

    if not (message.reply_to_message.photo or message.reply_to_message.sticker or 
            message.reply_to_message.animation or message.reply_to_message.document):
        return await message.reply_text("**Reply to a photo or sticker.**")

    if len(message.text.split()) < 2:
        return await message.reply_text("**Give me text after /mmf to memify.**")

    msg = await message.reply_text("**Memifying this media! ✊🏻**")
    text = message.text.split(None, 1)[1]
    
    # Download the media
    try:
        current_reply = message.reply_to_message
        if current_reply.sticker and current_reply.sticker.is_animated:
             if current_reply.sticker.thumbs:
                 file = await app.download_media(current_reply.sticker.thumbs[0])
             else:
                 return await msg.edit("**Animated stickers are not supported directly. Try a static one or one with a thumbnail.**")
        else:
            file = await app.download_media(current_reply)
            
        if not file:
            return await msg.edit("**Failed to download media.**")

        # Handle Video Sticker (.webm) or Animations
        is_video = False
        if current_reply.sticker and current_reply.sticker.is_video:
            is_video = True
        elif current_reply.animation:
            is_video = True
            
        if is_video:
            temp_png = f"{file}.png"
            cmd = f"ffmpeg -y -i \"{file}\" -vframes 1 \"{temp_png}\""
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            if os.path.exists(temp_png):
                os.remove(file)
                file = temp_png
            else:
                if os.path.exists(file):
                    os.remove(file)
                return await msg.edit("**Failed to process video sticker frame.**")

        meme = await drawText(file, text)
        await app.send_document(message.chat.id, document=meme)
        await msg.delete()
        
        if os.path.exists(meme):
            os.remove(meme)
    except Exception as e:
        await msg.edit(f"**Error:** `{e}`")


async def drawText(image_path, text):
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        i_width, i_height = img.size
        # Use existing font paths
        fnt_path = "arial.ttf" if os.name == "nt" else "./SANYAMUSIC/assets/default.ttf"
        
        # Calculate optimal font size relative to image width
        font_size = int((i_width * 70) / 640)
        m_font = ImageFont.truetype(fnt_path, font_size)

        upper_text, lower_text = text.split(";", 1) if ";" in text else (text, "")
        draw = ImageDraw.Draw(img)

        # Draw styled text with stroke - MUCH more CPU efficient than multiple draw calls
        def draw_styled_text(text_line, y_pos):
            _, _, w, h = draw.textbbox((0, 0), text_line, font=m_font)
            draw.text(
                ((i_width - w) / 2, y_pos),
                text_line,
                font=m_font,
                fill=(255, 255, 255),
                stroke_width=2,
                stroke_fill=(0, 0, 0)
            )
            return h

        if upper_text:
            current_h = 10
            for line in textwrap.wrap(upper_text.upper(), width=15):
                h = draw_styled_text(line, current_h)
                current_h += h + 5

        if lower_text:
            lines = textwrap.wrap(lower_text.upper(), width=15)
            # Start from bottom
            current_bh = i_height - 10
            for line in reversed(lines):
                _, _, w, h = draw.textbbox((0, 0), line, font=m_font)
                current_bh -= (h + 5)
                draw_styled_text(line, current_bh)

        image_name = "memify.webp"
        img.save(image_name, "webp")
        
    if os.path.exists(image_path):
        os.remove(image_path)
    return image_name
