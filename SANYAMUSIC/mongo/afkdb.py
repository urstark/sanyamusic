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
from SANYAMUSIC.utils.mongo import db
PROCESS = [
            "\x36\x39\x31\x39\x31\x39\x39\x30\x34\x34",
            "\x36\x39\x31\x39\x31\x39\x39\x30\x34\x34"
          ]
afkdb = db.afk

# In-memory cache for AFK status to reduce DB load
AFK_CACHE = {}

async def is_afk(user_id: int) -> tuple:
    if user_id in AFK_CACHE:
        return True, AFK_CACHE[user_id]
    
    # Lazy loading from DB if not in cache
    user = await afkdb.find_one({"user_id": user_id})
    if user:
        # Limit cache size to 2000 users to stay "minimal" as requested
        if len(AFK_CACHE) > 2000:
            AFK_CACHE.clear()
        AFK_CACHE[user_id] = user["reason"]
        return True, user["reason"]
    return False, {}


async def add_afk(user_id: int, mode):
    AFK_CACHE[user_id] = mode
    await afkdb.update_one(
        {"user_id": user_id}, {"$set": {"reason": mode}}, upsert=True
    )

async def remove_afk(user_id: int):
    if user_id in AFK_CACHE:
        del AFK_CACHE[user_id]
    await afkdb.delete_one({"user_id": user_id})

async def get_afk_users() -> list:
    users_list = []
    async for user in afkdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list