import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from urllib.parse import urlparse
import re

BOT_TOKEN = "1031262750:AAEJjg1tSDVhCqASxMadmbv5J-8aNn3Lo04"

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("سلام! لینک دانلود رو برام بفرست.")

async def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("لینک معتبر بفرست")
        return
    
    status_msg = await update.message.reply_text("⏬ در حال دانلود...")
    
    try:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
            filename = "downloaded_file"
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        await status_msg.edit_text("✅ دانلود شد! در حال ارسال...")
        
        with open(filepath, 'rb') as f:
            await update.message.reply_document(document=f, filename=filename)
        
        os.remove(filepath)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ خطا: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
