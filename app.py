import os
import logging
import requests
import base64
import io
import json
from flask import Flask, request, jsonify

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

def send_telegram_message(chat_id, text):
    """Send a text message via Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def send_telegram_photo(chat_id, photo_data, caption):
    """Send a photo via Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    try:
        files = {'photo': ('image.png', photo_data, 'image/png')}
        data = {
            'chat_id': chat_id,
            'caption': caption
        }
        
        response = requests.post(url, files=files, data=data, timeout=60)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return False

def send_telegram_photo_url(chat_id, photo_url, caption):
    """Send a photo by URL via Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending photo URL: {e}")
        return False

def generate_image(prompt):
    """Generate image using Stability AI API"""
    if not STABILITY_API_KEY:
        logger.warning("No Stability API key configured")
        return None
        
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
            result = response.json()
            if "artifacts" in result and len(result["artifacts"]) > 0:
                return result["artifacts"][0]["base64"]
        else:
            logger.error(f"Stability AI API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error generating image: {e}")
    
    return None

def handle_start_command(chat_id):
    """Handle /start command"""
    message = (
        "👋 <b>Welcome to Imagify Bot!</b>\n\n"
        "Send me any text prompt, and I'll generate an AI image for you 🎨✨\n\n"
        "<i>Example:</i> 'A cat wearing a space suit on Mars'"
    )
    send_telegram_message(chat_id, message)

def handle_text_message(chat_id, text):
    """Handle text message (image generation prompt)"""
    prompt = text.strip()
    
    # Send "generating" message
    send_telegram_message(chat_id, "🎨 Generating image... please wait ⏳")
    
    try:
        # Try to generate image with Stability AI
        image_base64 = generate_image(prompt)
        
        if image_base64:
            # Convert base64 to bytes and send
            image_data = base64.b64decode(image_base64)
            success = send_telegram_photo(
                chat_id, 
                io.BytesIO(image_data), 
                f"✨ Prompt: {prompt}"
            )
            
            if not success:
                send_telegram_message(chat_id, "❌ Failed to send generated image. Please try again.")
        else:
            # Fallback to placeholder image
            placeholder_url = f"https://picsum.photos/512/512?random={abs(hash(prompt)) % 1000}"
            success = send_telegram_photo_url(
                chat_id,
                placeholder_url,
                f"✨ Placeholder image for: {prompt}\n(AI generation temporarily unavailable)"
            )
            
            if not success:
                send_telegram_message(chat_id, "❌ Failed to generate image. Please try again later.")
                
    except Exception as e:
        logger.error(f"Error in handle_text_message: {e}")
        send_telegram_message(chat_id, "⚠️ Something went wrong while generating the image.")

# Flask webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhooks from Telegram"""
    try:
        update_data = request.get_json()
        
        if not update_data:
            return "No data", 400
        
        # Extract message info
        message = update_data.get("message")
        if not message:
            return "No message", 400
            
        chat_id = message.get("chat", {}).get("id")
        if not chat_id:
            return "No chat ID", 400
        
        # Handle different message types
        if "text" in message:
            text = message["text"]
            
            if text.startswith("/start"):
                handle_start_command(chat_id)
            else:
                handle_text_message(chat_id, text)
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route("/", methods=["GET"])
def health_check():
    status = "🤖 <b>Imagify Bot is running!</b><br><br>"
    
    if BOT_TOKEN:
        status += "✅ Bot token configured<br>"
    else:
        status += "❌ Bot token missing<br>"
        
    if STABILITY_API_KEY:
        status += "✅ Stability API key configured<br>"
    else:
        status += "⚠️ Stability API key missing (will use placeholder images)<br>"
    
    status += "<br>Send a message to the bot to start generating images!"
    
    return status, 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Set webhook URL (call this once after deployment)"""
    if not BOT_TOKEN:
        return "❌ BOT_TOKEN not configured", 500
        
    # Get the app URL from the request
    app_url = request.host_url.rstrip('/')
    webhook_url = f"{app_url}/webhook"
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            json={"url": webhook_url}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                return f"✅ Webhook set successfully to {webhook_url}", 200
            else:
                return f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}", 500
        else:
            return f"❌ HTTP Error: {response.status_code} - {response.text}", 500
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return f"❌ Error setting webhook: {str(e)}", 500

@app.route("/webhook_info", methods=["GET"])
def webhook_info():
    """Get current webhook information"""
    if not BOT_TOKEN:
        return "❌ BOT_TOKEN not configured", 500
        
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return f"❌ Error: {response.status_code} - {response.text}", 500
            
    except Exception as e:
        return f"❌ Error getting webhook info: {str(e)}", 500

@app.route("/test_stability", methods=["GET"])
def test_stability():
    """Test Stability AI API"""
    if not STABILITY_API_KEY:
        return "❌ STABILITY_API_KEY not configured", 500
    
    test_prompt = "a simple red apple"
    result = generate_image(test_prompt)
    
    if result:
        return "✅ Stability AI API is working", 200
    else:
        return "❌ Stability AI API test failed", 500

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ ERROR: Please set your BOT_TOKEN environment variable.")
    else:
        print("✅ Starting webhook server...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)