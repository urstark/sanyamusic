import asyncio
import random
import re
import aiohttp
import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from SANYAMUSIC import app, YouTube, LOGGER
from config import BANNED_USERS
from SANYAMUSIC.utils.database import is_active_chat
from SANYAMUSIC.utils.decorators.language import language, languageCB
from SANYAMUSIC.utils.exceptions import AssistantErr
from SANYAMUSIC.utils.database import get_cmode
from SANYAMUSIC.utils.formatters import time_to_seconds

RANDOM_HINDI_QUERIES = [
    "Insta tending", "Lofi songs", "Latest Hindi Songs", "Romantic Songs", 
    "Sad Songs", "Punjabi Hits", "Best of Arijit Singh", 
    "Atif Aslam Hits", "Old Hindi Songs", "90s Bollywood Songs",
    "Party Songs Hindi", "Indian Lo-fi"
]

def clean_text(title):
    title = re.sub(r'[\(\[].*?[\)\]]', '', title)
    if "|" in title:
        title = title.split("|")[0]
    if "-" in title:
        title = title.split("-")[0]
    return title.strip()

async def get_itunes_recommendations(title):
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Search for the track to get Artist ID
            async with session.get(
                "https://itunes.apple.com/search",
                params={"term": title, "entity": "song", "limit": 1}
            ) as resp:
                if resp.status != 200: return []
                search_data = await resp.json(content_type=None)
                results = search_data.get("results", [])
                
                if not results:
                    return [], None
                
                primary_genre = results[0].get("primaryGenreName")
            
            if not primary_genre:
                return [], None
            
            suggestions = []
            
            # 2. Get songs from the same genre
            async with session.get(
                "https://itunes.apple.com/search",
                params={"term": primary_genre, "entity": "song", "limit": 20}
            ) as resp2:
                if resp2.status == 200:
                    search_data2 = await resp2.json(content_type=None)
                    results2 = search_data2.get("results", [])
                    random.shuffle(results2)
                    for item in results2:
                        if item.get("wrapperType") == "track":
                            track_name = item.get("trackName")
                            artist_name = item.get("artistName")
                            # Filter out the searched title to avoid duplicates
                            if title.lower() not in track_name.lower():
                                suggestions.append(f"{track_name} - {artist_name}")
                            
                            if len(suggestions) >= 5:
                                break
            return suggestions, primary_genre
    except Exception as e:
        LOGGER(__name__).error(f"iTunes API Error: {e}")
        return [], None

async def show_suggestions(chat_id: int, last_played_title: str):
    """
    Shows song suggestions after 10 seconds if no song is playing.
    Call this function in your stream end handler.
    """
    # 1. Wait 20 seconds
    await asyncio.sleep(10)
    
    if await is_active_chat(chat_id):
        LOGGER(__name__).info(f"Chat {chat_id} is active, skipping suggestions.")
        return
    
    # 2. Fetch suggestions
    
    suggestions = []
    refresh_keyword = None
    
    # Try to get suggestions based on the last played song
    if last_played_title:
        clean_title = clean_text(last_played_title)
        if not clean_title:
            clean_title = last_played_title

        refresh_keyword = clean_title
        
        # 1. Get Genre Recommendations from iTunes
        itunes_recs, genre = await get_itunes_recommendations(clean_title)
        if itunes_recs:
            suggestions.extend(itunes_recs)
        else:
            # 2. Get Similar Songs from YouTube (Fallback)
            if genre:
                keyword = f"best {genre} songs similar to {clean_title}"
            else:
                keyword = f"songs similar to {clean_title}"
            
            youtube_recs = await YouTube.suggestions(keyword, limit=5)
            if youtube_recs:
                filtered_yt = [
                    s for s in youtube_recs
                    if clean_title.lower() not in s['title'].lower()
                ]
                suggestions.extend(filtered_yt)
            
        # Shuffle to mix Artist songs and Similar songs
        random.shuffle(suggestions)

    # If we still don't have enough, get random ones
    if len(suggestions) < 3:
        if last_played_title:
            keyword = clean_title
        else:
            keyword = random.choice(RANDOM_HINDI_QUERIES)
        needed = 3 - len(suggestions)
        # This returns dicts from YouTube
        new_suggestions = await YouTube.suggestions(keyword, limit=needed + 2)  # fetch extra for filtering
        if new_suggestions:
            filtered_new = [
                s for s in new_suggestions
                if not last_played_title or clean_text(last_played_title).lower() not in s['title'].lower()
            ]
            suggestions.extend(filtered_new)

    # Ensure unique suggestions and limit to 3
    final_suggestions = []
    seen = set()
    for s in suggestions:
        # Handle both Spotify strings and YouTube dicts
        val = s if isinstance(s, str) else s['id']
        if len(final_suggestions) < 3 and val not in seen:
            final_suggestions.append(s)
            seen.add(val)
    suggestions = final_suggestions

    if not suggestions:
        LOGGER(__name__).info(f"No suggestions found for chat {chat_id}.")
        return

    # 3. Build Buttons
    buttons = []
    for item in suggestions:
        if isinstance(item, str):
            # Spotify Suggestion (String)
            title_text = item[:30]
            # Truncate query for callback data to avoid limit (64 bytes)
            # "suggestion_query:" is 17 chars, leaving 47 chars.
            cb_data = f"suggestion_query:{item[:40]}"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}...",
                    callback_data=cb_data
                )
            ])
        else:
            # YouTube Suggestion (Dict)
            title_text = clean_text(item['title'])[:30]
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}... - {item['duration']}",
                    callback_data=f"suggestion_play:{item['id']}"
                )
            ])
    
    refresh_data = f"refresh_suggestions:{refresh_keyword}" if refresh_keyword else "refresh_suggestions"
    if len(refresh_data) > 64:
        refresh_data = f"refresh_suggestions:{refresh_keyword[:40]}"

    buttons.append([
        InlineKeyboardButton(text="Refresh", callback_data=refresh_data),
        InlineKeyboardButton(text="Close", callback_data="close")
    ])

    # 4. Send Message
    try:
        msg = await app.send_message(
            chat_id,
            text=f"<b>💿 No music is playing!</b>\n\n💡 <i>Use /suggest <code>sahiba</code> or /suggest for suggestions.</i>\n\nHere are some suggestions:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # 5. Delete after 1 minute
        await asyncio.sleep(60)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        LOGGER(__name__).error(f"Error sending suggestion message: {e}")

@app.on_message(filters.command("suggest") & ~BANNED_USERS)
@language
async def suggest_command(client, message, _):
    msg = await message.reply_text("🔎 Finding suggestions...")
    
    if len(message.command) > 1:
        keyword = message.text.split(None, 1)[1]
        refresh_data = f"refresh_suggestions:{keyword}"
        if len(refresh_data) > 64:
            refresh_data = "refresh_suggestions"
    else:
        keyword = random.choice(RANDOM_HINDI_QUERIES)
        refresh_data = "refresh_suggestions"

    suggestions = []
    
    # 1. iTunes (Genre)
    itunes_recs, genre = await get_itunes_recommendations(keyword)
    if itunes_recs:
        suggestions.extend(itunes_recs)
    else:
        # 2. YouTube (Similar)
        if genre:
            yt_query = f"best {genre} songs similar to {keyword}"
        else:
            yt_query = f"songs similar to {keyword}"
        youtube_recs = await YouTube.suggestions(yt_query, limit=5)
        if youtube_recs:
            filtered_yt = [
                s for s in youtube_recs
                if keyword.lower() not in s['title'].lower()
            ]
            suggestions.extend(filtered_yt)
    
    random.shuffle(suggestions)
    
    if not suggestions:
        return await msg.edit(f"Could not fetch suggestions for '{keyword}'. Please try again.")

    buttons = []
    for item in suggestions:
        if isinstance(item, str):
            title_text = item[:30]
            cb_data = f"suggestion_query:{item[:40]}"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}...",
                    callback_data=cb_data
                )
            ])
        else:
            title_text = clean_text(item['title'])[:30]
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}... - {item['duration']}",
                    callback_data=f"suggestion_play:{item['id']}"
                )
            ])
    
    buttons.append([
        InlineKeyboardButton(text="Refresh", callback_data=refresh_data),
        InlineKeyboardButton(text="Close", callback_data="close")
    ])

    await msg.edit_text(
        f"<b>🎼 Here are some suggestions for you:</b>\n\nBased on: <i>{keyword}</i>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"^refresh_suggestions") & ~BANNED_USERS)
@languageCB
async def refresh_suggestions_cb(client, cq, _):
    await cq.answer("Refreshing...", show_alert=False)
    
    if ":" in cq.data:
        keyword = cq.data.split(":", 1)[1]
        refresh_data = cq.data
    else:
        keyword = random.choice(RANDOM_HINDI_QUERIES)
        refresh_data = "refresh_suggestions"

    suggestions = []
    
    # 1. iTunes (Genre)
    itunes_recs, genre = await get_itunes_recommendations(keyword)
    if itunes_recs:
        suggestions.extend(itunes_recs)
    else:
        # 2. YouTube (Similar)
        if genre:
            yt_query = f"best {genre} songs similar to {keyword}"
        else:
            yt_query = f"songs similar to {keyword}"
        youtube_recs = await YouTube.suggestions(yt_query, limit=5)
        if youtube_recs:
            filtered_yt = [
                s for s in youtube_recs
                if keyword.lower() not in s['title'].lower()
            ]
            suggestions.extend(filtered_yt)
        
    random.shuffle(suggestions)
    
    if not suggestions:
        return await cq.answer("Could not fetch new suggestions. Please try again.", show_alert=True)

    buttons = []
    for item in suggestions:
        if isinstance(item, str):
            title_text = item[:30]
            cb_data = f"suggestion_query:{item[:40]}"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}...",
                    callback_data=cb_data
                )
            ])
        else:
            title_text = clean_text(item['title'])[:30]
            buttons.append([
                InlineKeyboardButton(
                    text=f"{title_text}... - {item['duration']}",
                    callback_data=f"suggestion_play:{item['id']}"
                )
            ])
    
    buttons.append([
        InlineKeyboardButton(text="Refresh", callback_data=refresh_data),
        InlineKeyboardButton(text="Close", callback_data="close")
    ])

    try:
        await cq.edit_message_text(
            f"<b>🎼 Here are some suggestions for you:</b>\n\nBased on: <i>{keyword}</i>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception:
        pass

@app.on_callback_query(filters.regex(r"^suggestion_play:") & ~BANNED_USERS)
@languageCB
async def suggestion_play_cb(client, cq, _):
    vid_id = cq.data.split(":")[1]
    await cq.answer("Processing...", show_alert=False)

    # Determine the chat_id for the voice call
    chat_id_for_stream = cq.message.chat.id
    channel = await get_cmode(chat_id_for_stream)
    if channel:
        chat_id_for_stream = channel

    user_id = cq.from_user.id
    user_name = cq.from_user.first_name

    mystic = await cq.message.reply_text(_["play_1"])

    try:
        details, track_id = await YouTube.track(vid_id, True)
    except Exception as e:
        return await mystic.edit_text(_["play_3"] + f"\n\nError: {e}")

    if details.get("duration_min"):
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, client.me.mention)
            )
    else:
        # For simplicity, we won't handle live streams from suggestions.
        return await mystic.edit_text("Live streams are not supported for suggestions.")

    try:
        from SANYAMUSIC.utils.stream.stream import stream
        await stream(
            client,
            _,
            mystic,
            user_id,
            details,  # result
            chat_id_for_stream,  # voice chat id
            user_name,
            cq.message.chat.id,  # original_chat_id
            video=None,  # audio only for now
            streamtype="youtube",
            forceplay=None,  # Don't force play
        )
    except AssistantErr as e:
        await mystic.edit_text(str(e))
        return
    except Exception as e:
        ex_type = type(e).__name__
        err = _["general_2"].format(ex_type)
        await mystic.edit_text(err)
        return

    await mystic.delete()
    await cq.message.delete()

@app.on_callback_query(filters.regex(r"^suggestion_query:") & ~BANNED_USERS)
@languageCB
async def suggestion_query_cb(client, cq, _):
    query = cq.data.split(":", 1)[1]
    await cq.answer("Processing...", show_alert=False)

    chat_id_for_stream = cq.message.chat.id
    channel = await get_cmode(chat_id_for_stream)
    if channel:
        chat_id_for_stream = channel

    user_id = cq.from_user.id
    user_name = cq.from_user.first_name

    mystic = await cq.message.reply_text(_["play_1"])

    try:
        # Search YouTube for the query string
        title, dur_min, dur_sec, thumb, vidid = await YouTube.details(query)
        # Get full track details using the ID found
        details, track_id = await YouTube.track(vidid, True)
    except Exception as e:
        return await mystic.edit_text(_["play_3"] + f"\n\nError: {e}")

    if details.get("duration_min"):
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, client.me.mention)
            )

    try:
        from SANYAMUSIC.utils.stream.stream import stream
        await stream(
            client,
            _,
            mystic,
            user_id,
            details,
            chat_id_for_stream,
            user_name,
            cq.message.chat.id,
            video=None,
            streamtype="youtube",
            forceplay=None,
        )
    except Exception as e:
        await mystic.edit_text(_["general_2"].format(type(e).__name__))
        return

    await mystic.delete()
    await cq.message.delete()
