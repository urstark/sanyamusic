from SANYAMUSIC import app
from pyrogram import filters, enums
from SANYAMUSIC.utils.Sanya_ban import admin_filter


@app.on_message(filters.command("unbanall") & admin_filter)
async def unban_all(_, msg):
    chat_id = msg.chat.id
    bot = await app.get_chat_member(chat_id, (await app.get_me()).id)
    
    if not bot.privileges or not bot.privileges.can_restrict_members:
        return await msg.reply_text(
            "I don't have the required permission to unban users. Make sure I am an admin and can restrict members."
        )

    await msg.reply_text("Trying to unban all banned users...")
    
    unbanned_count = 0
    async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BANNED):
        try:
            await app.unban_chat_member(chat_id, member.user.id)
            unbanned_count += 1
        except Exception as e:
            await msg.reply_text(f"Failed to unban {member.user.mention}: {e}")

    if unbanned_count == 0:
        await msg.reply_text("No banned users found to unban.")
    else:
        await msg.reply_text(f"Successfully unbanned {unbanned_count} user(s).")


@app.on_callback_query(filters.regex("^stop$"))
async def stop_callback(_, query):
    await query.message.delete()

###
