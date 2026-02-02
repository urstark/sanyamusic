import asyncio
import random
import time

from SANYAMUSIC import app
from config import OWNER_ID
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Safety & Performance
HARD_CAP_BANS_PER_SECOND = 5.0  # Absolute max bans/sec
DEFAULT_BANS_PER_SECOND = 2.0  # Default if no rate is specified
BANS_BEFORE_LONG_PAUSE = 40  # After this many bans, take a long pause
LONG_PAUSE_SECONDS = 10  # Long pause duration
BASE_JITTER = 0.5  # Random delay added to each ban


async def safe_edit(msg: Message, text: str):
    try:
        await msg.edit_text(text)
    except Exception:
        pass


@app.on_message(filters.command("banall") & filters.user(OWNER_ID))
async def ban_all_command(_, message):
    chat_id = message.chat.id
    # Extract optional rate limit from command, e.g., /banall 3
    rate = DEFAULT_BANS_PER_SECOND
    if len(message.command) > 1:
        try:
            rate = float(message.command[1])
            if rate > HARD_CAP_BANS_PER_SECOND:
                rate = HARD_CAP_BANS_PER_SECOND
        except ValueError:
            pass

    await message.reply_text(
        "** Are you sure you want to ban all members in this chat?**\n\nThis action is irreversible.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Yes, ban all", callback_data=f"ban_all_confirm|{chat_id}|{rate}"
                    ),
                    InlineKeyboardButton("Cancel", callback_data="ban_all_cancel"),
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex("^ban_all_confirm"))
async def ban_all_confirm(_, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("This is not for you!", show_alert=True)

    try:
        chat_id = int(query.data.split("|")[1])
        rate = float(query.data.split("|")[2])
    except (IndexError, ValueError):
        return await query.message.edit("Invalid callback data.")

    per_ban_delay = 1.0 / rate if rate > 0 else 1.0
    status_msg = await query.message.edit_text(
        f"Initializing... Starting safe banning at **{rate:.2f} bans/sec**."
    )

    try:
        me = await app.get_me()
        my_member = await app.get_chat_member(chat_id, me.id)
        if not my_member.privileges or not my_member.privileges.can_restrict_members:
            return await status_msg.edit(
                " **I don't have permission to ban members in this chat.**"
            )
    except Exception as e:
        return await status_msg.edit(f"An error occurred: {e}")

    banned_count = 0
    failed_count = 0
    batch_since_pause = 0
    flood_backoff = 0

    async for member in app.get_chat_members(chat_id):
        user_id = member.user.id
        # Skip the Owner, the bot itself, and other bots
        if user_id == OWNER_ID or user_id == me.id or member.user.is_bot:
            continue

        try:
            if flood_backoff > 0:
                await safe_edit(status_msg, f"FloodWait active — sleeping for {int(flood_backoff)}s...")
                await asyncio.sleep(flood_backoff)
                flood_backoff = 0

            await app.ban_chat_member(chat_id, user_id)
            banned_count += 1
            batch_since_pause += 1

            if banned_count % 10 == 0:
                await safe_edit(status_msg, f"Banned **{banned_count}** members...")

            if batch_since_pause >= BANS_BEFORE_LONG_PAUSE:
                batch_since_pause = 0
                await safe_edit(status_msg, f"Taking a long pause of {LONG_PAUSE_SECONDS}s...")
                await asyncio.sleep(LONG_PAUSE_SECONDS)

            jitter = random.random() * BASE_JITTER
            await asyncio.sleep(per_ban_delay + jitter)

        except FloodWait as fw:
            flood_backoff = min(fw.value * 1.5, 300)
            continue
        except Exception as e:
            failed_count += 1
            continue

    await status_msg.edit_text(
        f" **Ban All Complete!**\n\n**Successfully Banned:** `{banned_count}`\n**Failed Attempts:** `{failed_count}`"
    )


@app.on_callback_query(filters.regex("^ban_all_cancel$"))
async def ban_all_cancel_callback(_, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("This is not for you!", show_alert=True)
    await query.message.edit_text("Ban all operation cancelled.")
