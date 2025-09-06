# 🎨 Imagify Bot - AI Image Generation Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.11.9-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)](https://flask.palletsprojects.com/)
[![Heroku](https://img.shields.io/badge/Deploy-Heroku-purple.svg)](https://heroku.com)

A powerful Telegram bot that generates AI images from text prompts using multiple AI services for maximum reliability. Send any text description and get beautiful AI-generated images instantly!

## ✨ Features

- **🤖 Multiple AI Services**: Automatic fallback between Stability AI, Pollinations.ai, and Hugging Face
- **🚀 Fast & Reliable**: Smart service switching ensures high uptime
- **💰 Cost Effective**: Uses free services when premium APIs are unavailable
- **📱 Easy to Use**: Simple text-to-image generation via Telegram
- **🔧 Production Ready**: Built with Flask and designed for Heroku deployment
- **📊 Monitoring**: Health checks and service testing endpoints

## 🎯 Supported AI Services

| Service | Type | Quality | Speed | API Key Required |
|---------|------|---------|--------|------------------|
| **Stability AI** | Premium | ⭐⭐⭐⭐⭐ | Fast | ✅ Yes |
| **Pollinations.ai** | Free | ⭐⭐⭐⭐ | Fast | ❌ No |
| **Hugging Face** | Free Tier | ⭐⭐⭐ | Medium | ⚠️ Optional |

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token (looks like `123456789:ABCdefGhIJKlmNoPQRsTuVwXyZ`)

### 2. Get AI API Keys (Optional but Recommended)

**Stability AI** (Recommended for best quality):
- Sign up at [Stability AI](https://platform.stability.ai/)
- Get your API key from the dashboard

**Hugging Face** (Optional - free tier works without key):
- Sign up at [Hugging Face](https://huggingface.co/)
- Get your API token from [settings](https://huggingface.co/settings/tokens)

### 3. Deploy to Cloud Platforms

**Deploy to Render (Recommended):**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/your-repo-name)

**Deploy to Heroku:**

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

**Manual Deployment:**

```bash
# Clone the repository
git clone <your-repo-url>
cd imagify-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_bot_token_here"
export STABILITY_API_KEY="your_stability_key_here"  # Optional
export HUGGINGFACE_API_KEY="your_hf_token_here"    # Optional

# Run locally for testing
python app.py
```

**For Heroku deployment:**

```bash
# Create Heroku app
heroku create your-bot-name

# Set environment variables
heroku config:set BOT_TOKEN="your_bot_token_here"
heroku config:set STABILITY_API_KEY="your_stability_key_here"  # Optional

# Deploy
git push heroku main

# Set webhook (do this once after deployment)
curl https://your-bot-name.herokuapp.com/set_webhook
```

### 4. Set Up Webhook

After deployment, visit: `https://your-bot-name.herokuapp.com/set_webhook`

You should see: ✅ Webhook set successfully

## 📋 Environment Variables

Create a `.env` file or set these environment variables:

```env
BOT_TOKEN=your_telegram_bot_token_here
STABILITY_API_KEY=your_stability_ai_key_here          # Optional - for premium quality
HUGGINGFACE_API_KEY=your_huggingface_token_here       # Optional - for higher rate limits
```

## 🎮 How to Use

1. **Start the bot**: Send `/start` to your bot on Telegram
2. **Generate images**: Send any text description:
   - "A cat wearing a space suit on Mars"
   - "A fantasy castle in the clouds at sunset"
   - "A robot painting a beautiful landscape"
   - "A cyberpunk city with neon lights"

The bot will automatically:
- Show a "generating" message
- Try multiple AI services for best results
- Send you the generated image
- Provide fallback options if generation fails

## 🛠️ API Endpoints

Your deployed bot includes several useful endpoints:

| Endpoint | Description |
|----------|-------------|
| `/` | Health check and service status |
| `/webhook` | Telegram webhook receiver |
| `/set_webhook` | Set up Telegram webhook |
| `/webhook_info` | Get current webhook status |
| `/test_services` | Test all AI services |

## 📁 Project Structure

```
imagify-bot/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── runtime.txt        # Python version for Heroku
├── Procfile          # Heroku process configuration
├── .env              # Environment variables (create this)
└── README.md         # This file
```

## 🔧 Configuration

The bot intelligently handles different scenarios:

- **All services available**: Uses Stability AI first (best quality)
- **No premium keys**: Falls back to free services automatically
- **Service overload**: Tries alternative services seamlessly
- **All services down**: Provides helpful error message with retry suggestions

## 🚀 Advanced Features

### Service Priority

1. **Stability AI** - Used first if API key is available (best quality)
2. **Pollinations.ai** - Fast and reliable free service
3. **Hugging Face** - Backup free service

### Error Handling

- Automatic service switching on failure
- User-friendly error messages
- Retry suggestions
- Comprehensive logging

### Monitoring

- Health check endpoint for uptime monitoring
- Service testing endpoint for debugging
- Detailed logging for troubleshooting

## 🛡️ Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- The `.env` file is gitignored for security
- Bot token should be kept secret

## 📊 Performance Tips

1. **Use Stability AI key** for best image quality
2. **Monitor service status** via `/test_services`
3. **Check webhook health** periodically
4. **Use descriptive prompts** for better results

## 🔍 Troubleshooting

### Bot not responding?

**For Render:**
- Check `/webhook_info` endpoint
- View logs in Render dashboard
- Verify webhook: `https://your-app.onrender.com/set_webhook`
- Check if service is sleeping (shouldn't happen on Render)

**For Heroku:**
- Check `/webhook_info` endpoint  
- Check logs: `heroku logs --tail`
- App might be sleeping (free tier limitation)
- Ping app to wake it up

### Images not generating?
- Test services: `/test_services`
- Check API key validity
- Try simpler prompts

### Webhook issues?
- Re-run `/set_webhook`
- Check bot token is correct
- Verify app is deployed and running

## 🎨 Example Prompts

Get creative with these example prompts:

**Artistic Styles:**
- "Van Gogh style painting of a modern city"
- "Anime character in a magical forest"
- "Photorealistic portrait of a wise owl"

**Scenes & Landscapes:**
- "Sunset over a calm ocean with sailboats"
- "Ancient temple hidden in jungle ruins"
- "Futuristic space station orbiting Earth"

**Characters & Creatures:**
- "Friendly dragon reading a book"
- "Steampunk inventor in their workshop"
- "Cute robot learning to paint"

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section
2. Test your API keys
3. Review the logs
4. Create an issue with details

---

**Made with ❤️ for the AI art community**

*Generate amazing images with just a text message! 🎨✨*