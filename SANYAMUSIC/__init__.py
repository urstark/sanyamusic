# -----------------------------------------------
# 🔸 SanyaMusic Project
# 🔹 Developed & Maintained by: Stark (https://github.com/urstark)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by urstark
# -----------------------------------------------
from SANYAMUSIC.core.bot import SANYA
from SANYAMUSIC.core.dir import dirr
from SANYAMUSIC.core.git import git
from SANYAMUSIC.core.userbot import Userbot
from SANYAMUSIC.misc import dbb, heroku
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = SANYA()
userbot = Userbot()
api = SafoneAPI()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "InflexOwnerBot"  # connect music api key "Dont change it"