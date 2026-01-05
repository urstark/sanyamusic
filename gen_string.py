import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

async def generate_session():
    load_dotenv()
    print("--- Pyrogram String Session Generator ---")
    
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if not api_id or not api_hash:
        print("Get your API ID and API HASH from https://my.telegram.org")
        try:
            api_id = int(input("\nEnter API ID: "))
            api_hash = input("Enter API HASH: ")
        except ValueError:
            print("Invalid API ID. Please enter a valid integer.")
            return
    else:
        try:
            api_id = int(api_id)
        except ValueError:
            print("Invalid API ID in .env file.")
            return

    print("\nConnecting to Telegram...")
    print("Please enter your phone number when prompted (e.g., +919876543210)")
    
    async with Client(
        "sanyamusic_string",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    ) as app:
        session_string = await app.export_session_string()
        
        print("\n" + "=" * 50)
        print("YOUR STRING SESSION")
        print("=" * 50)
        print(f"\n{session_string}\n")
        print("=" * 50)
        
        try:
            await app.send_message("me", f"**Your String Session:**\n\n`{session_string}`")
            print("\n[+] Successfully sent the session string to your Saved Messages!")
        except Exception as e:
            print(f"\n[-] Failed to send to Saved Messages: {e}")

if __name__ == "__main__":
    asyncio.run(generate_session())
