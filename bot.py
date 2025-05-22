import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Config
API_ID = "12411512"
API_HASH = "0417d4f5fa67431b3c1b984a712cdbe3"
BOT_TOKEN = "6730490066:AAEMtyTH4OlpS3o9JXdd1KXmF-WX99LB5Xo"

# Init bot
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# TeraBox link parser (simple logic for public links)
def get_direct_link(terabox_url: str) -> str:
    api = "https://teraboxapp.com/api/openShare/info?shorturl="
    file_code = terabox_url.split("/")[-1]
    resp = requests.get(api + file_code)
    
    try:
        data = resp.json()
        fs_id = data['list'][0]['fs_id']
        share_id = data['shareid']
        uk = data['uk']
        dlink_api = f"https://teraboxapp.com/api/sharedownload?shareid={share_id}&uk={uk}&fsid_list=[{fs_id}]"
        dl_resp = requests.get(dlink_api)
        dlink = dl_resp.json()['list'][0]['dlink']
        return dlink
    except Exception as e:
        print("Error:", e)
        return None

# Handle TeraBox links
@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def terabox_handler(client: Client, message: Message):
    url = message.text.strip()
    if "terabox" not in url:
        await message.reply("Please send a valid TeraBox link.")
        return

    await message.reply("Processing your TeraBox link...")

    dlink = get_direct_link(url)
    if not dlink:
        await message.reply("Failed to extract the download link. It might be private or invalid.")
        return

    filename = dlink.split("/")[-1].split("?")[0]
    filepath = f"./downloads/{filename}"

    os.makedirs("downloads", exist_ok=True)

    try:
        r = requests.get(dlink, stream=True)
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        await message.reply_document(document=filepath, caption="Here's your file from TeraBox.")
        os.remove(filepath)
    except Exception as e:
        await message.reply(f"Error downloading or sending file: {e}")

# Start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply("Send me a TeraBox link, and I'll download the file for you!")

# Run the bot
app.run()
