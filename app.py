import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ✅ Enable logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Load Telegram Bot Token from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ✅ Tor proxy settings (port 9150 = Tor Browser)
proxies = {
    "http": "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150",
}

# Dummy free API (you can replace with Hugging Face / Stable Diffusion endpoint)
IMAGE_API_URL = "https://picsum.photos/512"  

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "👋 Welcome to Imagify Bot!\n\n"
            "Send me any text prompt, and I’ll generate an AI image for you 🎨✨"
        )

# Handle user prompts
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    prompt = update.message.text.strip()
    await update.message.reply_text("🎨 Generating image... please wait ⏳")

    try:
        # Example: get random image (replace with AI API call)
        response = requests.get(IMAGE_API_URL, proxies=proxies, timeout=30)

        if response.status_code == 200:
            await update.message.reply_photo(photo=response.url, caption=f"✨ Prompt: {prompt}")
        else:
            await update.message.reply_text("❌ Failed to generate image. Try again later.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Something went wrong while generating the image.")

# Main function
def main():
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Please set your TELEGRAM_TOKEN environment variable.")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))

    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()