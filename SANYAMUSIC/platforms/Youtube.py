import os
import re
import json
import random
import shutil
import asyncio
import yt_dlp
import aiofiles
import aiohttp
from typing import Union
from urllib.parse import unquote, urljoin
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

import config
from SANYAMUSIC import LOGGER
from SANYAMUSIC.utils.database import is_on_off
from SANYAMUSIC.utils.formatters import time_to_seconds, seconds_to_min


def cookie_txt_file():
    # Primary location for SanyaMusic
    original_cookie_path = "SANYAMUSIC/assets/cookies.txt"
    if os.path.exists(original_cookie_path):
        return original_cookie_path
    
    # Fallback to a 'cookies' directory if it exists
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    if os.path.exists(cookie_dir):
        cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt") and not f.endswith("example.txt")]
        if cookies_files:
            return os.path.join(cookie_dir, random.choice(cookies_files))
    
    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def _download_media(self, link: str, video: bool = False) -> str:
        media_type = "video" if video else "audio"
        ext = "mp4" if video else "m4a"

        video_id = (
            link.split("v=")[-1].split("&")[0] if "v=" in link else link.split("/")[-1]
        )

        if not video_id or len(video_id) < 3:
            return None

        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path):
            return file_path

        try:
            async with aiohttp.ClientSession() as session:
                search_url = f"{config.API_URL}/search"
                params = {"q": video_id, "type": media_type, "api_key": config.API_KEY}
                
                async with session.get(search_url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    stream_url_path = data.get("stream_url")
                    if not stream_url_path:
                        return None
                    
                    full_stream_url = urljoin(config.API_URL, stream_url_path)
                    
                    # Retry logic
                    for _ in range(15):
                        async with session.get(full_stream_url, timeout=20) as stream_res:
                            if stream_res.status == 200:
                                content_disposition = stream_res.headers.get("Content-Disposition", "")
                                match = re.search(r"filename\*=utf-8''([^;]+)", content_disposition)
                                if match:
                                    filename = unquote(match.group(1))
                                    file_path = os.path.join(DOWNLOAD_DIR, filename)
                                
                                async with aiofiles.open(file_path, "wb") as f:
                                    async for chunk in stream_res.content.iter_chunked(16384):
                                        await f.write(chunk)
                                return file_path if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else None
                            
                            elif stream_res.status == 202:
                                # Wait and retry as per API design
                                pass 
                            else:
                                break
                        
                        await asyncio.sleep(5)
        except Exception as e:
            LOGGER(__name__).error(f"Error in _download_media ({media_type}): {e}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        return None

    def _yt_dlp_call_with_fallback(self, action, opts):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return action(ydl)
        except Exception as e:
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise e

            opts_fallback = opts.copy()
            opts_fallback.update({
                "cookiefile": cookie_file,
                "cachedir": False,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            })
            with yt_dlp.YoutubeDL(opts_fallback) as ydl:
                return action(ydl)

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

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = (result.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
                vidid = result["id"]
                duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
                return title, duration_min, duration_sec, thumbnail, vidid
            return None, None, None, None, None
        except Exception as e:
            LOGGER(__name__).error(f"Error fetching details for {link}: {e}")
            return None, None, None, None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        _, duration, _, _, _ = await self.details(link, videoid)
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    async def video(
        self, link: str, videoid: Union[bool, str] = None, stream: bool = True
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        video_id = (
            link.split("v=")[-1].split("&")[0] if "v=" in link else link.split("/")[-1]
        )
        stream_type = "video" if stream else "audio"

        try:
            async with aiohttp.ClientSession() as session:
                search_url = f"{config.API_URL}/search"
                params = {"q": video_id, "type": stream_type, "api_key": config.API_KEY}
                
                async with session.get(search_url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        return 0, f"API Error: Status {resp.status}"
                    data = await resp.json()
                    stream_url_path = data.get("stream_url")
                    if not stream_url_path:
                        return 0, "API Error: No stream url."
                    
                    full_stream_url = urljoin(config.API_URL, stream_url_path)
                    
                    for _ in range(15):
                        async with session.get(full_stream_url, timeout=20) as stream_res:
                            if stream_res.status == 200:
                                return 1, full_stream_url
                            elif stream_res.status == 202:
                                pass
                            else:
                                return 0, "API Error: Failed to stream."
                        await asyncio.sleep(5)
        except Exception as e:
            LOGGER(__name__).error(f"Exception in video method for {link}: {e}")
            return 0, str(e)
            
        return 0, "API Error: Timeout waiting for stream"

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
        try:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                vidid = result["id"]
                yturl = result["link"]
                thumbnail = (result.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
                track_details = {
                    "title": title,
                    "link": yturl,
                    "vidid": vidid,
                    "duration_min": duration_min,
                    "thumb": thumbnail,
                }
                return track_details, vidid
            return None, None
        except Exception as e:
            try:
                cookie_file = cookie_txt_file()
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "format": "bestaudio/best",
                    "noplaylist": True,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                }
                if cookie_file:
                    ydl_opts["cookiefile"] = cookie_file

                search_query = link
                if not re.search(self.regex, link):
                     search_query = f"ytsearch1:{link}"

                def extract_info():
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(search_query, download=False)

                loop = asyncio.get_running_loop()
                info = await loop.run_in_executor(None, extract_info)
                
                if "entries" in info:
                    if not info["entries"]:
                        return None, None
                    info = info["entries"][0]
                
                title = info["title"]
                duration_min = seconds_to_min(info["duration"])
                vidid = info["id"]
                yturl = info.get("webpage_url", f"https://www.youtube.com/watch?v={vidid}")
                thumbnail = info.get("thumbnail")
                
                track_details = {
                    "title": title,
                    "link": yturl,
                    "vidid": vidid,
                    "duration_min": duration_min,
                    "thumb": thumbnail,
                }
                return track_details, vidid
            except Exception as e2:
                LOGGER(__name__).error(f"Error in track method for {link}: {e} | Fallback error: {e2}")
                return None, None

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
        if not result or len(result) <= query_type:
             return "Unknown Title", "0:00", None, None
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = (result[query_type].get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
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
                    "thumb": (item.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
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
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            self._yt_dlp_call_with_fallback(lambda ydl: ydl.download([link]), ydl_optssx)

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
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
            downloaded_file = await self._download_media(link, video=True)
            if downloaded_file:
                return downloaded_file, True
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4", True
        
        if songaudio:
            downloaded_file = await self._download_media(link, video=False)
            if downloaded_file:
                return downloaded_file, True
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3", True
        
        # Main logic for /play
        downloaded_file = None
        direct = None

        # 1. Try API stream (Disabled: unreliable with PyTgCalls)
        # if not await is_on_off(1):
        #     status, result = await self.video(link, stream=bool(video))
        #     if status == 1:
        #         downloaded_file = result
        #         direct = None

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
