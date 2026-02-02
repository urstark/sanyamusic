
import asyncio
import time
from pyrogram import Client, filters
#from googlesearch import search
from SANYAMUSIC import app

def google_search_sync(query, num_results):
    """Synchronous function to perform a Google search."""
    return list(search(query, num_results=num_results))

@app.on_message(filters.command("dork"))
async def dork(client, message):
    query = message.text.split(" ", 1)
    if len(query) == 1:
        await message.reply_text("🚫 𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘀𝗲𝗮𝗿𝗰𝗵 𝗾𝘂𝗲𝗿𝘆.\n\n /dork <your_query>")
        return

    dork_query = query[1]
    start_time = time.time()
    
    # Run the blocking search in a separate thread
    try:
        results = await asyncio.to_thread(google_search_sync, dork_query, 50)
    except Exception as e:
        await message.reply_text(f"Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴅᴜʀɪɴɢ ᴛʜᴇ sᴇᴀʀᴄʜ: {e}")
        return

    end_time = time.time()

    if results:
        results_text = "\n".join([f"{idx + 1}. {res}\n" for idx, res in enumerate(results)])
        time_taken = end_time - start_time

        # Create a .txt file with the query name and save the results
        file_name = f"{dork_query}.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(results_text)

        # Send the .txt file
        caption = (
            f"🔍 𝗚𝗼𝗼𝗴𝗹𝗲 𝗗𝗼𝗿𝗸 𝗥𝗲𝘀𝘂𝗹𝘁𝘀\n"
            f"⏱️ 𝗧𝗶𝗺𝗲 𝗧𝗮𝗸𝗲𝗻 : {time_taken:.2f} seconds\n"
            f"👤 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗯𝘆 : {message.from_user.first_name}"
        )

        await message.reply_document(file_name, caption=caption)
    else:
        await message.reply_text("ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ.")