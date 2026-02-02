import re
import httpx
from pyrogram import filters
from pyrogram.types import Message

# Assuming SANYAMUSIC is your Pyrogram Client object
from SANYAMUSIC import app

# --- Configuration (Move these to config.py if you have one) ---
try:
    from config import LOGGER_ID
except ImportError:
    LOGGER_ID = None
    
# From both files
DOWNLOADING_STICKER_ID = (
    "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
)
# Primary API for rich metadata (from instadl.py)
API_URL = "https://insta-dl.hazex.workers.dev" 
# Fallback API (from instadl2.py)
FALLBACK_API_URL = "https://karma-api2.vercel.app/instadl"

# Regex to match Instagram URLs (from instadl.py)
INSTA_URL_REGEX = re.compile(
    r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/"
)


async def _process_content(message: Message, url: str):
    """
    Helper function to process the Instagram URL and send the content (photo/video).
    (This function remains the same, as it contains the core download logic)
    """
    # 1. URL Validation
    if not re.match(INSTA_URL_REGEX, url):
        return await message.reply_text(
            "Tʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ URL ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL😅😅"
        )

    # 2. Status Update
    processing_msg = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")

    # Choose the primary API for rich metadata
    primary_api_url = f"{API_URL}/?url={url}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(primary_api_url, timeout=30)
            response.raise_for_status()
            result = response.json()

        # Check for API-level errors
        if result.get("error"):
            # If the primary API fails, try the fallback (simple) API
            raise Exception(result.get("message", "Primary API failed, trying fallback..."))

        data = result.get("result")
        if not data:
            raise Exception("No result data found in API response.")

    except Exception as e:
        # Fallback Logic (using the API from instadl2.py)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(FALLBACK_API_URL, params={"url": url}, timeout=30)
                response.raise_for_status()
                data = response.json()
            
            # Simple content URL extraction (from instadl2.py)
            if "content_url" in data:
                content_url = data["content_url"]
                caption = "Dᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ Fᴀʟʟʙᴀᴄᴋ API."
                
                # Determine content type (from instadl2.py)
                if "video" in content_url:
                    await message.reply_video(content_url, caption=caption)
                else:
                    await message.reply_photo(content_url, caption=caption)
                
                await processing_msg.delete()
                return
            else:
                raise Exception("Fallback API failed to provide a content URL.")

        except Exception as fallback_e:
            # If both APIs fail
            error_message = f"Eʀʀᴏʀ :\n{fallback_e}"
            try:
                await processing_msg.edit_text(error_message)
            except Exception:
                await message.reply_text(error_message)
            if LOGGER_ID:
                await app.send_message(LOGGER_ID, f"INSTADL FAILED for {url}:\n{fallback_e}")
            return


    # --- Primary API Success Processing ---
    if data.get("url"):
        content_url = data["url"]
        duration = data.get("duration", "N/A")
        quality = data.get("quality", "N/A")
        type_ext = data.get("extension", "N/A")
        size = data.get("formattedSize", "N/A")
        
        # Determine if it's a photo or video based on the extension/type
        is_video = True if type_ext.lower() in ["mp4", "webm", "mov"] else False

        caption = f"Dᴜʀᴀᴛɪᴏɴ : {duration}\nQᴜᴀʟɪᴛʏ : {quality}\nTʏᴘᴇ : {type_ext}\nSɪᴢᴇ : {size}"

        try:
            if is_video:
                await message.reply_video(content_url, caption=caption)
            else:
                await message.reply_photo(content_url, caption=caption)
            
            await processing_msg.delete()
        except Exception as e:
            error_message = f"Eʀʀᴏʀ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ᴄᴏɴᴛᴇɴᴛ:\n{e}"
            await processing_msg.edit_text(error_message)
            if LOGGER_ID:
                await app.send_message(LOGGER_ID, error_message)
    else:
        # Handle case where primary API call was successful but URL wasn't found
        try:
            return await processing_msg.edit_text(
                "Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ. Nᴏ ᴄᴏɴᴛᴇɴᴛ URL Fᴏᴜɴᴅ."
            )
        except Exception:
            return await message.reply_text(
                "Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ. Nᴏ ᴄᴏɴᴛᴇɴᴛ URL Fᴏᴜɴᴅ."
            )


@app.on_message(filters.command(["ig", "insta", "instagram", "reel"]))
async def download_instagram_command(client, message: Message):
    """
    Handles Instagram downloads exclusively via command.
    """
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ."
        )
        return

    # Extract the URL from the message
    url = message.text.split(None, 1)[1].strip()
    
    if not url:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ."
        )
        return

    await _process_content(message, url)

# *** The 'download_instagram_no_command' function has been removed. ***
