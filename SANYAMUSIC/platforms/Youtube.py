import asyncio
import os
import re
import shutil
from typing import Union

import yt_dlp 
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
import aiohttp

import config
from SANYAMUSIC import LOGGER
from SANYAMUSIC.utils.database import is_on_off
from SANYAMUSIC.utils.formatters import time_to_seconds, seconds_to_min

API_URL = "https://shrutibots.site"

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def _download_media(self, link: str, video: bool = False) -> str:
        media_type = "video" if video else "audio"
        ext = "mp4" if video else "mp3"
        timeout = 600 if video else 300

        video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link.split('/')[-1]

        if not video_id or len(video_id) < 3:
            return None

        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path):
            return file_path

        try:
            async with aiohttp.ClientSession() as session:
                params = {"url": video_id, "type": media_type}
                
                async with session.get(f"{API_URL}/download", params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200: return None
                    data = await response.json()
                    download_token = data.get("download_token")
                    if not download_token: return None
                    
                    stream_url = f"{API_URL}/stream/{video_id}?type={media_type}&token={download_token}"
                    
                    async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=timeout)) as file_response:
                        if file_response.status == 302:
                            redirect_url = file_response.headers.get('Location')
                            if redirect_url:
                                async with session.get(redirect_url) as final_response:
                                    if final_response.status != 200: return None
                                    with open(file_path, "wb") as f:
                                        async for chunk in final_response.content.iter_chunked(16384):
                                            f.write(chunk)
                                    return file_path if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else None
                        elif file_response.status == 200:
                            with open(file_path, "wb") as f:
                                async for chunk in file_response.content.iter_chunked(16384):
                                    f.write(chunk)
                            return file_path if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else None
                        return None
        except Exception as e:
            LOGGER(__name__).error(f"Error in _download_media ({media_type}): {e}")
            if os.path.exists(file_path):
                try: os.remove(file_path)
                except: pass
            return None

    def _yt_dlp_call_with_fallback(self, action, opts):
        """
        A synchronous wrapper for yt-dlp calls that falls back to using cookies.
        'action' is a lambda like: lambda ydl: ydl.extract_info(link, download=False)
        """
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return action(ydl)
        except Exception as e:
            original_cookie_path = "SANYAMUSIC/assets/cookies.txt"
            if not os.path.exists(original_cookie_path):
                raise e

            temp_cookie_path = "SANYAMUSIC/assets/cookies_temp.txt"
            shutil.copy2(original_cookie_path, temp_cookie_path)
            
            opts_fallback = opts.copy()
            opts_fallback.update({
                "cookiefile": temp_cookie_path,
                "cachedir": False,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            })
            try:
                with yt_dlp.YoutubeDL(opts_fallback) as ydl:
                    return action(ydl)
            finally:
                if os.path.exists(temp_cookie_path):
                    os.remove(temp_cookie_path)

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    # --- UPDATED: Uses the new API for all metadata fetching ---
    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    # --- UPDATED: Now uses the details method ---
    async def title(self, link: str, videoid: Union[bool, str] = None):
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    # --- UPDATED: Now uses the details method ---
    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, duration, _, _, _ = await self.details(link, videoid)
        return duration

    # --- UPDATED: Now uses the details method ---
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None, stream: bool = True):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link.split('/')[-1]
        stream_type = "video" if stream else "audio"

        try:
            async with aiohttp.ClientSession() as session:
                params = {"url": video_id, "type": stream_type}
                async with session.get(f"{API_URL}/download", params=params, timeout=10) as response:
                    if response.status != 200:
                        LOGGER(__name__).error(f"API /download failed for {link} with status {response.status}")
                        return 0, "API Error: Failed to get download token."
                    
                    data = await response.json()
                    download_token = data.get("download_token")
                    
                    if not download_token:
                        LOGGER(__name__).error(f"API /download no token for {link}")
                        return 0, "API Error: No download token in response."
                    
                    stream_url = f"{API_URL}/stream/{video_id}?type={stream_type}&token={download_token}"
                    
                    async with session.get(stream_url, timeout=15, allow_redirects=False) as file_response:
                        if file_response.status == 302:
                            redirect_url = file_response.headers.get('Location')
                            if redirect_url:
                                return 1, redirect_url
                        return 1, stream_url
        except Exception as e:
            LOGGER(__name__).error(f"Exception in video method for {link}: {e}")
            return 0, str(e)


    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
            
        proc = await asyncio.create_subprocess_shell(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, errorz = await proc.communicate()
        if errorz:
            if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
                output = out.decode("utf-8")
            else:
                output = errorz.decode("utf-8")
        else:
            output = out.decode("utf-8")

        try:
            result = output.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
            
        def get_fmt():
            opts = {"quiet": True, "no_warnings": True}
            info = self._yt_dlp_call_with_fallback(
                lambda ydl: ydl.extract_info(link, download=False),
                opts,
            )
            
            formats_available = []
            for format in info.get("formats", []):
                try:
                    if "dash" not in str(format.get("format")).lower():
                        formats_available.append(
                            {
                                "format": format.get("format"),
                                "filesize": format.get("filesize"),
                                "format_id": format.get("format_id"),
                                "ext": format.get("ext"),
                                "format_note": format.get("format_note"),
                                "yturl": link,
                            }
                        )
                except:
                    continue
            return formats_available

        loop = asyncio.get_running_loop()
        formats_available = await loop.run_in_executor(None, get_fmt)
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def suggestions(self, keyword: str, limit: int = 2):
        try:
            results = VideosSearch(keyword, limit=limit + 5)
            data = (await results.next())["result"]
            suggestions = []
            for item in data:
                suggestions.append({
                    "title": item["title"],
                    "id": item["id"],
                    "duration": item["duration"],
                    "thumb": item["thumbnails"][0]["url"].split("?")[0]
                })
            return suggestions[1 : limit + 1]
        except Exception:
            return []

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        # For /song command
        def song_video_dl():
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats, "outtmpl": fpath, "geo_bypass": True,
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True, "merge_output_format": "mp4",
            }
            self._yt_dlp_call_with_fallback(lambda ydl: ydl.download([link]), ydl_optssx)

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id, "outtmpl": fpath, "geo_bypass": True,
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            }
            self._yt_dlp_call_with_fallback(lambda ydl: ydl.download([link]), ydl_optssx)

        # yt-dlp fallback for /play
        def audio_dl_fallback():
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "no_warnings": True,
            }
            def action(ydl):
                info = ydl.extract_info(link, download=False)
                filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(filepath):
                    ydl.download([link])
                return filepath
            return self._yt_dlp_call_with_fallback(action, ydl_optssx)

        def video_dl_fallback():
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "no_warnings": True,
            }
            def action(ydl):
                info = ydl.extract_info(link, download=False)
                filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(filepath):
                    ydl.download([link])
                return filepath
            return self._yt_dlp_call_with_fallback(action, ydl_optssx)

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"
        
        if songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"
        
        # Main logic for /play
        downloaded_file = None
        direct = None

        # 1. Try API stream (if not in direct download mode)
        if not await is_on_off(1):
            status, result = await self.video(link, stream=bool(video))
            if status == 1:
                downloaded_file = result
                direct = None

        # 2. Try API download (if streaming failed or in direct download mode)
        if not downloaded_file:
            direct = True
            downloaded_file = await self._download_media(link, video=bool(video))

        # 3. Fallback to yt-dlp download if API fails completely
        if not downloaded_file:
            direct = True
            LOGGER(__name__).warning(f"API failed for {link}. Falling back to yt-dlp download.")
            if video:
                downloaded_file = await loop.run_in_executor(None, video_dl_fallback)
            else:
                downloaded_file = await loop.run_in_executor(None, audio_dl_fallback)

        return downloaded_file, direct
