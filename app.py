import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# Create Flask app (this is what Gunicorn needs)
app = Flask(__name__)

# Create Telegram application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Image generation using Stability AI (since you have the API key)
def generate_image(prompt):
    """Generate image using Stability AI API"""
    try:
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 512,
            "width": 512,
            "samples": 1,
            "steps": 30,
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return response.json()["artifacts"][0]["base64"]
        else:
            logger.error(f"Stability AI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "👋 Welcome to Imagify Bot!\n\n"
            "Send me any text prompt, and I'll generate an AI image for you 🎨✨\n\n"
            "Example: 'A cat wearing a space suit on Mars'"
        )

# Handle user prompts
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    prompt = update.message.text.strip()
    await update.message.reply_text("🎨 Generating image... please wait ⏳")

    try:
        # Generate image using Stability AI
        image_base64 = generate_image(prompt)
        
        if image_base64:
            import base64
            import io
            
            # Convert base64 to bytes
            image_data = base64.b64decode(image_base64)
            
            # Send photo
            await update.message.reply_photo(
                photo=io.BytesIO(image_data), 
                caption=f"✨ Prompt: {prompt}"
            )
        else:
            await update.message.reply_text("❌ Failed to generate image. Try again later.")

    except Exception as e:
        logger.error(f"Error in generate: {e}")
        await update.message.reply_text("⚠️ Something went wrong while generating the image.")

# Add handlers to telegram app
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))

# Flask webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhooks from Telegram"""
    try:
        update = Update.de_json(request.get_json(), telegram_app.bot)
        telegram_app.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!", 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Set webhook URL (call this once after deployment)"""
    webhook_url = f"https://your-app-name.onrender.com/webhook"
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            json={"url": webhook_url}
        )
        if response.status_code == 200:
            return f"Webhook set successfully to {webhook_url}", 200
        else:
            return f"Failed to set webhook: {response.text}", 500
    except Exception as e:
        return f"Error setting webhook: {e}", 500

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ ERROR: Please set your BOT_TOKEN environment variable.")
    else:
        print("✅ Starting webhook server...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))