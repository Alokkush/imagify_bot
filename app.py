import os
import logging
import requests
import base64
import io
import json
from flask import Flask, request, jsonify
from urllib.parse import quote

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Optional

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

def generate_image_huggingface(prompt):
    """Generate image using Hugging Face API (Free tier available)"""
    try:
        # Using Stable Diffusion model on Hugging Face
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        
        headers = {}
        if HUGGINGFACE_API_KEY:
            headers["Authorization"] = f"Bearer {HUGGINGFACE_API_KEY}"
        
        payload = {"inputs": prompt}
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.content  # Returns image bytes directly
        else:
            logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating image with Hugging Face: {e}")
        return None

def generate_image_stability(prompt):
    """Generate image using Stability AI API"""
    if not STABILITY_API_KEY:
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
                return base64.b64decode(result["artifacts"][0]["base64"])
        else:
            logger.error(f"Stability AI API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error generating image with Stability: {e}")
    
    return None

def generate_image_pollinations(prompt):
    """Generate image using Pollinations AI (Free service)"""
    try:
        # Pollinations.ai free API
        url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Pollinations API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating image with Pollinations: {e}")
        return None

def generate_image(prompt):
    """Try multiple AI services to generate an image"""
    logger.info(f"Generating image for prompt: {prompt}")
    
    # Try Stability AI first (if API key available)
    if STABILITY_API_KEY:
        logger.info("Trying Stability AI...")
        image_data = generate_image_stability(prompt)
        if image_data:
            logger.info("Stability AI succeeded")
            return image_data
    
    # Try Pollinations AI (free)
    logger.info("Trying Pollinations AI...")
    image_data = generate_image_pollinations(prompt)
    if image_data:
        logger.info("Pollinations AI succeeded")
        return image_data
    
    # Try Hugging Face (free tier)
    logger.info("Trying Hugging Face...")
    image_data = generate_image_huggingface(prompt)
    if image_data:
        logger.info("Hugging Face succeeded")
        return image_data
    
    logger.warning("All AI services failed")
    return None

def handle_start_command(chat_id):
    """Handle /start command"""
    message = (
        "👋 <b>Welcome to Imagify Bot!</b>\n\n"
        "Send me any text prompt, and I'll generate an AI image for you 🎨✨\n\n"
        "<i>Examples:</i>\n"
        "• 'A cat wearing a space suit on Mars'\n"
        "• 'A fantasy castle in the clouds'\n"
        "• 'A robot painting a sunset'\n\n"
        "✨ <b>Powered by multiple AI services for best results!</b>"
    )
    send_telegram_message(chat_id, message)

def handle_text_message(chat_id, text):
    """Handle text message (image generation prompt)"""
    prompt = text.strip()
    
    # Send "generating" message
    send_telegram_message(chat_id, "🎨 Generating your AI image... please wait ⏳")
    
    try:
        # Try to generate image with multiple AI services
        image_data = generate_image(prompt)
        
        if image_data:
            # Send the generated image
            success = send_telegram_photo(
                chat_id, 
                io.BytesIO(image_data), 
                f"✨ <b>Generated:</b> {prompt}\n\n🤖 <i>Made with AI</i>"
            )
            
            if not success:
                send_telegram_message(chat_id, "❌ Failed to send generated image. Please try again.")
        else:
            # All AI services failed - send a nice fallback message
            send_telegram_message(
                chat_id, 
                f"😔 Sorry, I couldn't generate an image for:\n<i>'{prompt}'</i>\n\n"
                f"🔄 Please try:\n"
                f"• A simpler prompt\n"
                f"• Waiting a moment and trying again\n"
                f"• Different wording\n\n"
                f"💡 The AI services might be busy right now!"
            )
                
    except Exception as e:
        logger.error(f"Error in handle_text_message: {e}")
        send_telegram_message(chat_id, "⚠️ Something went wrong while generating the image. Please try again!")

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
        status += "⚠️ Stability API key missing<br>"
        
    if HUGGINGFACE_API_KEY:
        status += "✅ Hugging Face API key configured<br>"
    else:
        status += "ℹ️ Hugging Face API key missing (will use free tier)<br>"
    
    status += "<br>🎨 <b>Available AI Services:</b><br>"
    status += "• Stability AI (if key provided)<br>"
    status += "• Pollinations.ai (free)<br>"
    status += "• Hugging Face (free tier)<br>"
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

@app.route("/test_services", methods=["GET"])
def test_services():
    """Test all AI image generation services"""
    results = {}
    test_prompt = "a simple red apple"
    
    # Test Stability AI
    if STABILITY_API_KEY:
        stability_result = generate_image_stability(test_prompt)
        results["stability_ai"] = "✅ Working" if stability_result else "❌ Failed"
    else:
        results["stability_ai"] = "⚠️ No API key"
    
    # Test Pollinations
    pollinations_result = generate_image_pollinations(test_prompt)
    results["pollinations"] = "✅ Working" if pollinations_result else "❌ Failed"
    
    # Test Hugging Face
    hf_result = generate_image_huggingface(test_prompt)
    results["hugging_face"] = "✅ Working" if hf_result else "❌ Failed"
    
    return jsonify(results)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ ERROR: Please set your BOT_TOKEN environment variable.")
    else:
        print("✅ Starting webhook server...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)