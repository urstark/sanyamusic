import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from motor.motor_asyncio import AsyncIOMotorClient
from SANYAMUSIC import app
from SANYAMUSIC.misc import SUDOERS
from strings import get_string
from SANYAMUSIC.utils.database import get_lang
from config import API_ID, API_HASH, MONGO_DB_URI

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.SANYAMUSIC
clonedb = db.clones
cloneconfig = db.cloneconfig

clone_bot_clients = {}
CLONE_LIMIT = 1  # Set the limit of clones per user here

async def is_clone_enabled():
    setting = await cloneconfig.find_one({"setting": "clone"})
    if not setting:
        return False  # Disabled by default
    return setting.get("status") == "on"

async def enable_cloning():
    await cloneconfig.update_one({"setting": "clone"}, {"$set": {"status": "on"}}, upsert=True)

async def disable_cloning():
    await cloneconfig.update_one({"setting": "clone"}, {"$set": {"status": "off"}}, upsert=True)

@app.on_message(filters.command("clone") & filters.private)
async def clone_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /clone [BOT_TOKEN]\n\nOr forward a message from BotFather with the token.")
    
    token = message.command[1]
    await clone_process(token, message)

@app.on_message(filters.forwarded & filters.private)
async def clone_forward(client, message):
    if message.forward_from and message.forward_from.username == "BotFather":
        if message.text:
            token_search = re.search(r'([0-9]{8,10}:[a-zA-Z0-9_-]{35})', message.text)
            if token_search:
                token = token_search.group(1)
                await clone_process(token, message)
            else:
                await message.reply_text("<b>Error:</b> Could not find a bot token in the forwarded message.")

async def clone_process(token, message):
    if not await is_clone_enabled():
        return await message.reply_text("<b>Cloning is currently disabled by the bot owner.</b>")
    user_id = message.from_user.id
    count = await clonedb.count_documents({"user_id": user_id})
    if count >= CLONE_LIMIT:
        return await message.reply_text(f"<b>Error:</b> You have reached the limit of {CLONE_LIMIT} cloned bot(s). Use /delclone to remove one first.")

    status_msg = await message.reply_text("<b>Cloning...</b>\n\nPlease wait while I set up your bot.")
    
    try:
        # Verify the token with a temporary client
        temp_client = Client(
            f"temp_{token}", 
            api_id=API_ID, 
            api_hash=API_HASH, 
            bot_token=token, 
            in_memory=True
        )
        await temp_client.start()
        bot_info = await temp_client.get_me()
        await temp_client.stop()
        
        # Save clone details to database
        await clonedb.update_one(
            {"bot_id": bot_info.id},
            {"$set": {
                "token": token,
                "user_id": message.from_user.id,
                "username": bot_info.username,
                "name": bot_info.first_name
            }},
            upsert=True
        )
        
        # Start the cloned client permanently
        new_client = Client(
            f"clone_{bot_info.id}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token,
            in_memory=True
        )
        for group, handlers in app.dispatcher.groups.items():
            for handler in handlers:
                new_client.add_handler(handler, group)

        # Inject owner ID into the client instance
        new_client.owner_id = message.from_user.id
        await new_client.start()
        try:
            await new_client.join_chat("https://t.me/+Qghzd0P820E1MTI1")
        except Exception:
            pass
        try:
            await new_client.get_users(message.from_user.id)
        except Exception:
            pass
        clone_bot_clients[bot_info.id] = new_client
        
        await status_msg.edit_text(
            f"<b>Bot Cloned Successfully!</b>\n\n"
            f"<b>Bot Name:</b> {bot_info.first_name}\n"
            f"<b>Username:</b> @{bot_info.username}\n"
            f"<b>Owner ID:</b> {message.from_user.id}\n\n"
            f"You can now use your cloned bot."
        )
        
    except Exception as e:
        await status_msg.edit_text(f"<b>Cloning Failed:</b>\n\n<code>{e}</code>")

@app.on_message(filters.command("rmbot") & filters.private)
async def delete_cloned_bot(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /rmbot [BOT_TOKEN]")
    
    token = message.command[1]
    user_id = message.from_user.id
    
    clone_data = await clonedb.find_one({"token": token, "user_id": user_id})
    if not clone_data:
        return await message.reply_text("<b>Error:</b> No cloned bot found with this token belonging to you.")
    
    if clone_data['bot_id'] in clone_bot_clients:
        try:
            await clone_bot_clients[clone_data['bot_id']].stop()
        except Exception:
            pass
        del clone_bot_clients[clone_data['bot_id']]
        
    await clonedb.delete_one({"token": token})
    await message.reply_text("<b>Success:</b> Cloned bot removed.")

@app.on_message(filters.command(["delclone", "removeclone", "deleteclone"]) & filters.private)
async def delete_clone_command(client, message):
    user_id = message.from_user.id
    # Find all clones for the user
    cursor = clonedb.find({"user_id": user_id})
    clones = await cursor.to_list(length=None)
    
    if not clones:
        return await message.reply_text("<b>Error:</b> You don't have a cloned bot.")
    
    for clone in clones:
        if clone['bot_id'] in clone_bot_clients:
            await clone_bot_clients[clone['bot_id']].stop()
            del clone_bot_clients[clone['bot_id']]
        
    await clonedb.delete_many({"user_id": user_id})
    await message.reply_text("<b>Success:</b> Your cloned bot has been deleted.")

@app.on_message(filters.command("restartclone") & filters.private)
async def restart_clone_command(client, message):
    user_id = message.from_user.id
    clone_data = await clonedb.find_one({"user_id": user_id})
    if not clone_data:
        return await message.reply_text("<b>Error:</b> You don't have a cloned bot.")
    
    msg = await message.reply_text("<b>Restarting your cloned bot...</b>")
    
    # Restart all clones for the user
    cursor = clonedb.find({"user_id": user_id})
    async for clone_data in cursor:
        if clone_data['bot_id'] in clone_bot_clients:
            try:
                await clone_bot_clients[clone_data['bot_id']].stop()
            except Exception:
                pass
            del clone_bot_clients[clone_data['bot_id']]
        
        try:
            new_client = Client(
                f"clone_{clone_data['bot_id']}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=clone_data['token'],
                in_memory=True
            )
            for group, handlers in app.dispatcher.groups.items():
                for handler in handlers:
                    new_client.add_handler(handler, group)

            new_client.owner_id = user_id
            await new_client.start()
            try:
                await new_client.join_chat("https://t.me/+Qghzd0P820E1MTI1")
            except Exception:
                pass
            try:
                await new_client.get_users(user_id)
            except Exception:
                pass
            clone_bot_clients[clone_data['bot_id']] = new_client
        except Exception as e:
            await msg.edit_text(f"<b>Error:</b> Failed to restart a clone.\n\n<code>{e}</code>")
            
    await msg.edit_text("<b>Success:</b> Cloned bots restarted successfully.")

@app.on_message(filters.command(["mybot", "myclone"]) & filters.private)
async def check_cloned_command(client, message):
    user_id = message.from_user.id
    clone_data = await clonedb.find_one({"user_id": user_id})
    if not clone_data:
        return await message.reply_text("<b>Error:</b> You don't have a cloned bot.")
    
    text = "<b>Your Cloned Bots:</b>\n\n"
    async for clone in clonedb.find({"user_id": user_id}):
        text += (
            f"<b>Name:</b> {clone['name']}\n"
            f"<b>Username:</b> @{clone['username']}\n"
            f"<b>Token:</b> <code>{clone['token']}</code>\n\n"
        )
    await message.reply_text(text)

@app.on_message(filters.command("clonebroadcast") & SUDOERS)
async def broadcast_clones(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /clonebroadcast [MESSAGE]")
    
    text = message.text.split(None, 1)[1]
    sent = 0
    failed = 0
    sent_users = set()
    msg = await message.reply_text("<b>Broadcasting...</b>")
    
    async for clone in clonedb.find():
        user_id = clone['user_id']
        if user_id in sent_users:
            continue
        
        try:
            await app.send_message(user_id, f"<b>📢 Broadcast to Clone Owners:</b>\n\n{text}")
            sent += 1
            sent_users.add(user_id)
        except Exception:
            failed += 1
            
    await msg.edit_text(f"<b>Broadcast Complete:</b>\n\n<b>Sent:</b> {sent}\n<b>Failed:</b> {failed}")

@app.on_message(filters.command(["cloned", "totalbots"]) & SUDOERS)
async def total_clones(client, message):
    count = await clonedb.count_documents({})
    await message.reply_text(f"<b>Total Cloned Bots:</b> {count}")

@app.on_message(filters.command("clonedinfo") & SUDOERS)
async def cloned_info(client, message):
    count = await clonedb.count_documents({})
    if count == 0:
        return await message.reply_text("No cloned bots found.")
    
    text = "<b>Cloned Bots Information:</b>\n\n"
    async for clone in clonedb.find():
        text += f"<b>Name:</b> {clone['name']}\n<b>Username:</b> @{clone['username']}\n<b>Owner ID:</b> {clone['user_id']}\n<b>Bot ID:</b> {clone['bot_id']}\n\n"
    
    if len(text) > 4096:
        with open("clones.txt", "w", encoding="utf-8") as f:
            f.write(text.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", ""))
        await message.reply_document("clones.txt")
        os.remove("clones.txt")
    else:
        await message.reply_text(text)

@app.on_message(filters.command("delallclone") & SUDOERS)
async def delete_all_clones(client, message):
    msg = await message.reply_text("<b>Deleting all clones...</b>")
    
    for bot_id, cl_client in list(clone_bot_clients.items()):
        try:
            await cl_client.stop()
        except Exception:
            pass
        del clone_bot_clients[bot_id]
        
    await clonedb.delete_many({})
    await msg.edit_text("<b>Success:</b> All cloned bots and databases have been deleted.")

@app.on_callback_query(filters.regex("clone_panel"))
async def clone_panel(_, CallbackQuery):
    await CallbackQuery.answer()
    try:
        language = await get_lang(CallbackQuery.message.chat.id)
        _ = get_string(language)
    except:
        _ = get_string("en")
    
    text = _["clone_help"]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings_back_helper")]
    ])
    await CallbackQuery.edit_message_text(text, reply_markup=keyboard)

@app.on_message(filters.command("cloning") & SUDOERS)
async def clone_enable_disable(client, message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> /cloning [enable|disable]")
    
    state = message.command[1].lower()
    if state == "enable":
        if await is_clone_enabled():
            return await message.reply_text("✅ Cloning is already enabled.")
        await enable_cloning()
        await message.reply_text("✅ Cloning has been enabled.")
    elif state == "disable":
        if not await is_clone_enabled():
            return await message.reply_text("✅ Cloning is already disabled.")
        await disable_cloning()
        await message.reply_text("✅ Cloning has been disabled.")
    else:
        await message.reply_text("<b>Usage:</b> /cloning [enable|disable]")

async def restart_clones():
    await asyncio.sleep(10)
    async for clone in clonedb.find():
        try:
            client = Client(
                f"clone_{clone['bot_id']}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=clone['token'],
                in_memory=True
            )
            for group, handlers in app.dispatcher.groups.items():
                for handler in handlers:
                    client.add_handler(handler, group)

            client.owner_id = clone['user_id']
            await client.start()
            try:
                await client.join_chat("https://t.me/+Qghzd0P820E1MTI1")
            except Exception:
                pass
            try:
                await client.get_users(clone['user_id'])
            except Exception:
                pass
            clone_bot_clients[clone['bot_id']] = client
            await asyncio.sleep(1)
        except Exception:
            print(f"[Clone Error] Failed to restart clone for user {clone['user_id']}:")
            # Optional: Automatically remove invalid tokens
            # if "AccessTokenInvalid" in str(e):
            #     await clonedb.delete_one({"user_id": clone['user_id']})

# Schedule the restart of clones when the plugin is loaded
loop = asyncio.get_event_loop()
loop.create_task(restart_clones())

__module__ = "Clone"
__help__ = """**Clone Bot:**

✧ `/clone [bot_token]` : Clone a music bot.
✧ `/rmbot [bot_token]` : Remove a cloned bot.
✧ `/delclone` : Delete your cloned bot.
✧ `/mybot` : Check your cloned bot details."""
