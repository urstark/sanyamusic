# Kivo's Chatbot Database Logic, adapted for Sanya

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC

def get_db():
    return db


async def is_chatbot_on(chat_id: int) -> bool:
    """Check if chatbot is enabled for a chat."""
    chat = await get_db().groups.find_one({"chat_id": chat_id})
    # Disabled by default
    if not chat:
        return False
    return chat.get("chatbot_enabled", False)


async def chatbot_on(chat_id: int):
    """Enable chatbot for a chat."""
    await get_db().groups.update_one(
        {"chat_id": chat_id}, {"$set": {"chatbot_enabled": True}}, upsert=True
    )


async def chatbot_off(chat_id: int):
    """Disable chatbot for a chat."""
    await get_db().groups.update_one(
        {"chat_id": chat_id}, {"$set": {"chatbot_enabled": False}}, upsert=True
    )


async def get_user_history(user_id: int):
    """Get a user's chat history."""
    user = await get_db().chatbot.find_one({"user_id": user_id})
    return user["history"] if user else []


async def update_user_history(user_id: int, history: list):
    """Update a user's chat history."""
    await get_db().chatbot.update_one(
        {"user_id": user_id}, {"$set": {"history": history}}, upsert=True
    )


async def reset_user_history(user_id: int):
    """Reset a user's chat history."""
    await get_db().chatbot.update_one(
        {"user_id": user_id}, {"$set": {"history": []}}, upsert=True
    )
