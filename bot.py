import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup

# Config
API_ID = "12411512"
API_HASH = "0417d4f5fa67431b3c1b984a712cdbe3"
BOT_TOKEN = "6730490066:AAEMtyTH4OlpS3o9JXdd1KXmF-WX99LB5Xo"

# Init Pyrogram Client
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to get direct download link from TeraBox public link
def extract_download_url(terabox_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(terabox_url, headers=headers)
        if response.status_code != 200:
            return None

        html = response.text
        # Extract JSON from within the page
        match = re.search(r'window\.context\s*=\s*({.*?});', html)
        if not match:
            return None

        json_data = match.group(1)
        json_data = eval(json_data)  # Use eval carefully (only trusted input)

        # Get file link
        dlink = json_data['fileList'][0].get('dlink') or json_data['fileList'][0].get('downloadURL')
        filename = json_data['fileList'][0].get('filename', 'file')

        return dlink, filename
    except Exception as e:
        print("Error:", e)
        return None

# Telegram Handler
@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_link(client: Client, message: Message):
    url = message.text.strip()
    if not url.startswith("http") or "terabox" not in url:
        await message.reply("Please send a valid TeraBox link.")
        return

    await message.reply("🔄 Fetching your file...")

    result = extract_download_url(url)
    if not result:
        await message.reply("❌ Failed to extract download link. It might be private or invalid.")
        return

    dlink, filename = result
    filepath = f"./downloads/{filename}"
    os.makedirs("downloads", exist_ok=True)

    try:
        with requests.get(dlink, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        await message.reply_document(document=filepath, caption="✅ Here's your file from TeraBox.")
        os.remove(filepath)
    except Exception as e:
        await message.reply(f"❌ Error downloading or sending file: {e}")

# /start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply("👋 Send me a TeraBox link, and I'll download the file for you!")

# Start the bot
app.run()
