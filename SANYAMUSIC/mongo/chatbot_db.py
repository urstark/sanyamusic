# Kivo's Chatbot Database Logic, adapted for Sanya

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC

# Cache for chatbot status
CHATBOT_CACHE = {}

def get_db():
    return db

async def is_chatbot_on(chat_id: int) -> bool:
    if chat_id in CHATBOT_CACHE:
        return CHATBOT_CACHE[chat_id]
    
    # Lazy load when first checked
    chat = await get_db().groups.find_one({"chat_id": chat_id})
    if chat:
        if len(CHATBOT_CACHE) > 2000:
            CHATBOT_CACHE.clear()
        val = chat.get("chatbot_enabled", False)
        CHATBOT_CACHE[chat_id] = val
        return val
    return False

async def chatbot_on(chat_id: int):
    CHATBOT_CACHE[chat_id] = True
    await get_db().groups.update_one(
        {"chat_id": chat_id}, {"$set": {"chatbot_enabled": True}}, upsert=True
    )

async def chatbot_off(chat_id: int):
    CHATBOT_CACHE[chat_id] = False
    await get_db().groups.update_one(
        {"chat_id": chat_id}, {"$set": {"chatbot_enabled": False}}, upsert=True
    )


async def get_user_history(user_id: int):
    user = await get_db().chatbot.find_one({"user_id": user_id})
    return user["history"] if user else []


async def update_user_history(user_id: int, history: list):
    await get_db().chatbot.update_one(
        {"user_id": user_id}, {"$set": {"history": history}}, upsert=True
    )


async def reset_user_history(user_id: int):
    await get_db().chatbot.update_one(
        {"user_id": user_id}, {"$set": {"history": []}}, upsert=True
    )
