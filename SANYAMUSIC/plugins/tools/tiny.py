
import os
import json
import asyncio
import cv2
from PIL import Image
import shutil
from pyrogram import Client, filters
from SANYAMUSIC import app


@app.on_message(filters.command("tiny"))
async def tiny_sticker(client, message):
    reply = message.reply_to_message
    if not (reply and reply.sticker):
        await message.reply("Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ")
        return

    status_message = await message.reply("Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    await status_message.edit_text("🐾")

    ik = None
    file = None
    try:
        ik = await app.download_media(reply)
        im1 = Image.open("SANYAMUSIC/assets/shashank.png")

        if ik.endswith(".tgs"):
            if not shutil.which("lottie_convert.py"):
                await status_message.edit("`lottie_convert.py` not found. Please install `lottie-converter` (`pip install lottie-converter`).")
                if ik and os.path.exists(ik):
                    os.remove(ik)
                return

            await app.download_media(reply, "wel2.tgs")
            
            process1 = await asyncio.create_subprocess_shell("lottie_convert.py wel2.tgs json.json", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process1.wait()

            with open("json.json", "r") as json_file:
                jsn = json.load(json_file)
                jsn['w'] = 2000
                jsn['h'] = 2000
            with open("json.json", "w") as json_file:
                json.dump(jsn, json_file)

            process2 = await asyncio.create_subprocess_shell("lottie_convert.py json.json wel2.tgs", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process2.wait()

            file = "wel2.tgs"
            os.remove("json.json")

        elif ik.endswith((".gif", ".mp4", ".webm")):
            iik = cv2.VideoCapture(ik)
            _, busy = iik.read()
            cv2.imwrite("i.png", busy)
            fil = "i.png"
            im = Image.open(fil)
            z, d = im.size
            if z == d:
                xxx, yyy = 200, 200
            else:
                t = z + d
                a = z / t
                b = d / t
                aa = (a * 100) - 50
                bb = (b * 100) - 50
                xxx = 200 + 5 * aa
                yyy = 200 + 5 * bb
            k = im.resize((int(xxx), int(yyy)))
            k.save("k.png", format="PNG", optimize=True)
            im2 = Image.open("k.png")
            back_im = im1.copy()
            back_im.paste(im2, (150, 0))
            back_im.save("o.webp", "WEBP", quality=95)
            file = "o.webp"
            os.remove(fil)
            os.remove("k.png")
        else:
            im = Image.open(ik)
            z, d = im.size
            if z == d:
                xxx, yyy = 200, 200
            else:
                t = z + d
                a = z / t
                b = d / t
                aa = (a * 100) - 50
                bb = (b * 100) - 50
                xxx = 200 + 5 * aa
                yyy = 200 + 5 * bb
            k = im.resize((int(xxx), int(yyy)))
            k.save("k.png", format="PNG", optimize=True)
            im2 = Image.open("k.png")
            back_im = im1.copy()
            back_im.paste(im2, (150, 0))
            back_im.save("o.webp", "WEBP", quality=95)
            file = "o.webp"
            os.remove("k.png")
        
        if file and os.path.exists(file):
            await app.send_document(message.chat.id, file, reply_to_message_id=message.id)
            await status_message.delete()
        else:
            await status_message.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴛʜᴇ ᴛɪɴʏ sᴛɪᴄᴋᴇʀ.")

    except Exception as e:
        await status_message.edit(f"Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")
    finally:
        # Cleanup files
        if file and os.path.exists(file):
            os.remove(file)
        if ik and os.path.exists(ik):
            os.remove(ik)