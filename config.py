import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables
load_dotenv()

# Required credentials
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
GROQ_API_KEY = getenv("GROQ_API_KEY", None)
GROQ_MODEL = getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_FALLBACK_MODEL = getenv("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant")
GROQ_WHISPER_MODEL = getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")

COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())

# Bot and owner info
OWNER_USERNAME = getenv("OWNER_USERNAME")
BOT_USERNAME = getenv("BOT_USERNAME")
BOT_NAME = getenv("BOT_NAME", "Sanya")
ASSUSERNAME = getenv("ASSUSERNAME", "SANYAassistant")
MUST_JOIN = getenv("MUST_JOIN", "urstarkz")
BASE_URL = "https://api.waifu.pics"

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI")

# Limits and IDs
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
LOGGER_ID = int(getenv("LOGGER_ID"))
OWNER_ID = int(getenv("OWNER_ID"))
POST_CHANNEL_ID = int(getenv("POST_CHANNEL_ID", "-1003192209705"))

# Heroku
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
DEEP_API = getenv("DEEP_API")

# Git
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/urstark/sanyamusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)

# Support
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/LuxeKernel")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/SanyaxSupport")

# Mini App
MINI_APP_URL = getenv("MINI_APP_URL", "https://sanyamusic.vercel.app")

# Assistant settings
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))

# Song download limits
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

# Spotify
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

# Playlist limit
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Telegram file limits
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

# Session strings
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)
STRING6 = getenv("STRING_SESSION6", None)
STRING7 = getenv("STRING_SESSION7", None)

# Miscellaneous
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

DEBUG_IGNORE_LOG = True

###### IMAGE URLS ######

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/3sbjl5.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/7bb907999ea7156227283.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
STATS_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/3sbjl5.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/3sbjl5.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/3sbjl5.jpg"

# API Keys (Moved from plugins to secure them)
GPT_API_KEY = getenv("GPT_API_KEY", "62152c3c83c0e23c52d4478fbb105491e72dc21d12d1fdbec294658a5494b15e")
NUMVERIFY_API_KEY = getenv("NUMVERIFY_API_KEY", "f66950368a61ebad3cba9b5924b4532d")
GOOGLE_SEARCH_KEY = getenv("GOOGLE_SEARCH_KEY", "AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM")

# Helper function
def time_to_seconds(time: str) -> int:
    """Convert time string (MM:SS) to total seconds."""
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

# Calculate total duration limit in seconds
DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# Validate URLs
if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is invalid. It must start with https://")

if SUPPORT_CHAT and not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is invalid. It must start with https://")
