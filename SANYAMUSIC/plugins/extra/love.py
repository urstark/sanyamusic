import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from SANYAMUSIC import app

def get_random_message(love_percentage):
    """Returns a witty message based on the calculated percentage."""
    if love_percentage <= 30:
        return random.choice([
            "Love is in the air but needs a little spark.",
            "A good start but there's room to grow.",
            "It's just the beginning of something beautiful."
        ])
    elif love_percentage <= 70:
        return random.choice([
            "A strong connection is there. Keep nurturing it.",
            "You've got a good chance. Work on it.",
            "Love is blossoming, keep going."
        ])
    else:
        return random.choice([
            "Wow! It's a match made in heaven!",
            "Perfect match! Cherish this bond.",
            "Destined to be together. Congratulations!"
        ])

@app.on_message(filters.command("love", prefixes="/") & filters.group)
async def love_command(client, message):
    chat_id = message.chat.id
    
    # 1. Identify the 'Subject' (The person who needs a partner)
    user1 = None
    
    # Priority 1: Check if the command is a reply to someone
    if message.reply_to_message:
        user1 = message.reply_to_message.from_user
    
    # Priority 2: Check if a user was tagged/mentioned (e.g., /love @username)
    elif len(message.command) > 1:
        input_user = message.command[1]
        try:
            # Resolves the mention or ID into a full user object
            user1 = await client.get_users(input_user)
        except Exception:
            return await message.reply_text("I couldn't find that user. Please make sure the tag is correct.")
    
    # Priority 3: Default to the person who sent the command
    else:
        user1 = message.from_user

    # 2. Get a random partner (User 2)
    list_of_users = []
    try:
        # Scanning 200 members to ensure a diverse selection in larger groups
        # without causing heavy API lag for the music player.
        async for i in client.get_chat_members(chat_id, limit=200):
            if not i.user.is_bot and i.user.id != user1.id:
                list_of_users.append(i.user)
        
        if not list_of_users:
            return await message.reply_text("I couldn't find anyone else in this group to pair them with!")

        # Randomly select the partner from the pool
        user2 = random.choice(list_of_users)
        
        # 3. Calculation and Message Generation
        love_percentage = random.randint(10, 100)
        love_message = get_random_message(love_percentage)

        # 4. Final Formatting
        response = (
            f"**﹝⌬﹞ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛɪᴏɴ**\n\n"
            f"{user1.mention} 💕 + {user2.mention} 💕 = **{love_percentage}%**\n\n"
            f"{love_message}"
        )
        
        await message.reply_text(response)

    except Exception as e:
        # Log error to console for debugging
        print(f"Love Command Error: {e}")
