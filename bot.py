import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from urllib.parse import urlparse
import re

BOT_TOKEN = "bottoken"

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# شمارنده برای نام‌گذاری فایل‌ها
counter = 1

def get_next_filename(original_filename):
    """ساخت نام جدید با حفظ پسوند"""
    global counter
    
    # استخراج پسوند فایل
    extension = ""
    if '.' in original_filename:
        extension = original_filename[original_filename.rindex('.'):]
    
    # ساخت نام جدید با شمارنده
    new_filename = f"{counter}{extension}"
    
    # افزایش شمارنده
    counter += 1
    
    return new_filename

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 ربات دانلودر\n"
        "لینک دانلود بفرستید تا فایل رو دانلود کنم\n"
        "اسم فایل به صورت 1.apk , 2.apk , 3.apk ... ذخیره میشه"
    )

async def handle_message(update: Update, context: CallbackContext):
    global counter
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ لطفاً یک لینک معتبر بفرستید")
        return
    
    status_msg = await update.message.reply_text("⏬ در حال دانلود...")
    
    try:
        # استخراج نام اصلی فایل و پسوند آن
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # ساخت نام جدید با حفظ پسوند
        new_filename = get_next_filename(original_filename)
        
        # دانلود فایل
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(DOWNLOAD_DIR, new_filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        await status_msg.edit_text(f"✅ دانلود شد! نام فایل: {new_filename}\n📤 در حال ارسال...")
        
        # ارسال فایل با نام جدید
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f, 
                filename=new_filename,
                caption=f"📁 فایل شما\n🔹 نام جدید: {new_filename}\n🔹 نام اصلی: {original_filename}"
            )
        
        # پاک کردن فایل موقت
        os.remove(filepath)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ خطا: {str(e)}")

async def reset_counter(update: Update, context: CallbackContext):
    """دستور برای ریست شمارنده به 1"""
    global counter
    counter = 1
    await update.message.reply_text("✅ شمارنده ریست شد! فایل بعدی با نام 1.apk ذخیره میشه")

async def show_counter(update: Update, context: CallbackContext):
    """نمایش شمارنده فعلی"""
    await update.message.reply_text(f"📊 شمارنده فعلی: {counter}\nفایل بعدی با نام {counter}.پسوند ذخیره میشه")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_counter))
    app.add_handler(CommandHandler("counter", show_counter))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 ربات روشن شد...")
    print("💡 دستورات:")
    print("   /reset   - ریست شمارنده به 1")
    print("   /counter - نمایش شمارنده فعلی")
    app.run_polling()

if __name__ == "__main__":
    main()
