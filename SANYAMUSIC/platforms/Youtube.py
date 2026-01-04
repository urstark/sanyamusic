import asyncio
import os
import re
from typing import Union

import yt_dlp 
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

import httpx

import config
from SANYAMUSIC.utils.database import is_on_off
from SANYAMUSIC.utils.formatters import time_to_seconds, seconds_to_min

API_URL = "https://api.nubcoder.com/info"

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.http_client = httpx.AsyncClient(timeout=10.0) 

    async def _fetch_api_data(self, link: str) -> dict:
        """Central function to call the NubCoder API and return JSON data."""
        params = {"token": config.YT_API_TOKEN, "q": link}
        try:
            response = await self.http_client.get(API_URL, params=params)
            response.raise_for_status() 
            data = response.json()
            return data
        except httpx.HTTPError as e:
            raise Exception("Could not connect to the streaming service. It may be temporarily offline.")
        except Exception as e:
            raise Exception(f"The streaming service gave an invalid response: {e}")

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
            
        if not re.search(self.regex, link):
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                vidid = result["id"]
                duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid

        try:
            data = await self._fetch_api_data(link)
            title = data["title"]
            duration_sec = data["duration"]
            duration_min = seconds_to_min(duration_sec)
            thumbnail = data["thumbnail"]
            vidid = data["video_id"]
        except Exception:
            # Fallback to local yt-dlp with cookies if API fails
            opts = {"cookiefile": "SANYAMUSIC/assets/cookies.txt", "quiet": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                title = info.get("title")
                duration_sec = info.get("duration", 0)
                duration_min = seconds_to_min(duration_sec)
                thumbnail = info.get("thumbnail")
                vidid = info.get("id")
        
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

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            data = await self._fetch_api_data(link)
            video_url = data["url"]
            if video_url:
                return 1, video_url
            else:
                return 0, "API Error: Video stream URL was not found in the response."
        except Exception as e:
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
            
        if not re.search(self.regex, link):
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

        try:
            data = await self._fetch_api_data(link)
            track_details = {
                "title": data["title"],
                "link": data["youtube_link"],
                "vidid": data["video_id"],
                "duration_min": seconds_to_min(data["duration"]),
                "thumb": data["thumbnail"],
            }
            return track_details, data["video_id"]
        except Exception:
            # Fallback to local yt-dlp with cookies if API fails
            opts = {"cookiefile": "SANYAMUSIC/assets/cookies.txt", "quiet": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                track_details = {
                    "title": info.get("title"),
                    "link": info.get("webpage_url"),
                    "vidid": info.get("id"),
                    "duration_min": seconds_to_min(info.get("duration", 0)),
                    "thumb": info.get("thumbnail"),
                }
                return track_details, info.get("id")

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
            
        formats_available = []
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

        def audio_dl():
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": "SANYAMUSIC/assets/cookies.txt",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": "SANYAMUSIC/assets/cookies.txt",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

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
                "cookiefile": "SANYAMUSIC/assets/cookies.txt",
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

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
                "cookiefile": "SANYAMUSIC/assets/cookies.txt",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        
        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            return fpath
        
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath
        
        elif video:
            if await is_on_off(1):
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                status, result = await self.video(link)
                if status == 1:
                    downloaded_file = result
                    direct = None 
                else:
                    direct = True
                    downloaded_file = await loop.run_in_executor(None, video_dl)
        
        else:
            direct = True
            downloaded_file = await loop.run_in_executor(None, audio_dl)
            
        return downloaded_file, direct
