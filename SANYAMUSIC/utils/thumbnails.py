import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# Constants
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Layout Constants for 'thumbnails.py' Style ---
# The base image is 1280x720

THUMB_SIZE = 400
THUMB_BORDER = 20
THUMB_X = 120
THUMB_Y = 160

TEXT_X = 565
TITLE_Y = 180
META_Y = 320
BAR_Y = 380
ICONS_Y = 450

LINE_LENGTH = 580
RED_FILL_RATIO = 0.6  # 60% red fill as in thumbnails.py logic
CIRCLE_RADIUS = 10

# --- Helper Functions from 'thumbnails.py' ---

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

def crop_center_circle(img, output_size, border, crop_scale=0.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    
    # 1. Crop a large square from the center
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    
    # 2. Resize to fit the final circle size (minus border)
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    # 3. Create a white border image
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    
    # 4. Create the mask for the thumbnail (inner circle)
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    # 5. Paste the thumbnail onto the white border image using the mask
    final_img.paste(img, (border, border), mask_main)
    
    # 6. Create the final mask (outer circle for transparency)
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    # 7. Composite with a fully transparent image to apply the outer circular mask
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    
    return result

# The trim_to_width function from thumbnails2.py is no longer needed

async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v4.png")
    if os.path.exists(cache_path):
        return cache_path

    # YouTube video data fetch
    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        results_data = await results.next()
        result_items = results_data.get("result", [])
        if not result_items:
            raise ValueError("No results found.")
        data = result_items[0]
        title = re.sub(r"\W+", " ", data.get("title", "Unsupported Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
        channel = data.get("channel", {}).get("name", "Unknown Channel")
    except Exception:
        title, thumbnail, duration, views, channel = "Unsupported Title", YOUTUBE_IMG_URL, None, "Unknown Views", "Unknown Channel"

    is_live = not duration or str(duration).strip().lower() in {"", "live", "live now"}
    duration_text = "Live" if is_live else duration or "Unknown Mins"

    # Download thumbnail
    thumb_path = os.path.join(CACHE_DIR, f"thumb{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    # Create base image
    base = Image.open(thumb_path)
    
    # Resize and blur background (BoxBlur(20) from thumbnails.py)
    bg = base.resize((1280, 720)).convert("RGBA")
    bg = bg.filter(ImageFilter.BoxBlur(20))
    bg = ImageEnhance.Brightness(bg).enhance(0.6) # Enhance(0.6) from thumbnails.py

    # Draw details
    draw = ImageDraw.Draw(bg)
    try:
        # Load fonts as per thumbnails.py
        arial_font = ImageFont.truetype("SANYAMUSIC/assets/assets/font2.ttf", 30)
        regular_font = ImageFont.truetype("SANYAMUSIC/assets/assets/font.ttf", 30)
        title_font = ImageFont.truetype("SANYAMUSIC/assets/assets/font3.ttf", 45)
    except OSError:
        arial_font = regular_font = title_font = ImageFont.load_default()

    # 1. Apply Circular Thumbnail
    youtube_thumb = Image.open(thumb_path)
    circle_thumbnail = crop_center_circle(youtube_thumb, THUMB_SIZE, THUMB_BORDER)
    bg.paste(circle_thumbnail, (THUMB_X, THUMB_Y), circle_thumbnail)

    # 2. Draw Text (White color)
    title1, title2 = truncate(title)
    
    draw.text((TEXT_X, TITLE_Y), title1, fill=(255, 255, 255), font=title_font)
    draw.text((TEXT_X, TITLE_Y + 50), title2, fill=(255, 255, 255), font=title_font) # 50px offset
    
    draw.text((TEXT_X, META_Y), f"{channel}  |  {views}", fill=(255, 255, 255), font=arial_font)

    # 3. Progress bar
    red_length = int(LINE_LENGTH * RED_FILL_RATIO)

    # Draw Red Line (width=9 from thumbnails.py)
    start_point_red = (TEXT_X, BAR_Y)
    end_point_red = (TEXT_X + red_length, BAR_Y)
    draw.line([start_point_red, end_point_red], fill="red", width=9)

    # Draw White/Gray Line (width=8 from thumbnails.py)
    start_point_white = (TEXT_X + red_length, BAR_Y)
    end_point_white = (TEXT_X + LINE_LENGTH, BAR_Y)
    draw.line([start_point_white, end_point_white], fill="white", width=8) # Used white as in thumbnails.py

    # Draw Red Circle
    circle_position = (end_point_red[0], end_point_red[1])
    draw.ellipse([circle_position[0] - CIRCLE_RADIUS, circle_position[1] - CIRCLE_RADIUS,
                  circle_position[0] + CIRCLE_RADIUS, circle_position[1] + CIRCLE_RADIUS], fill="red")

    # Draw time texts
    draw.text((TEXT_X, BAR_Y + 20), "00:00", fill=(255, 255, 255), font=arial_font) # 20px offset
    
    # Calculate X position for end time (1080 from thumbnails.py)
    end_time_x = 1080 
    draw.text((end_time_x, BAR_Y + 20), duration_text, fill=(255, 255, 255) if not is_live else "red", font=arial_font)

    # 4. Icons
    icons_path = "SANYAMUSIC/assets/assets/play_icons.png"
    if os.path.isfile(icons_path):
        ic = Image.open(icons_path)
        ic = ic.resize((LINE_LENGTH, 62)) # Resized to LINE_LENGTH (580) and 62px height
        bg.paste(ic, (TEXT_X, ICONS_Y), ic)

    # Cleanup and save
    try:
        os.remove(thumb_path)
    except OSError:
        pass

    bg.save(cache_path)
    return cache_path
