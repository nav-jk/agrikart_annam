#  AgriKart WhatsApp Bot

This is the WhatsApp integration service for **AgriKart.ai**, allowing Indian farmers to interact with the platform using **voice or text messages over WhatsApp**. It handles onboarding, produce listings, market price prediction, weather queries, and AI-powered agri Q&A — all through a simple WhatsApp chat.

---

##  Features

- WhatsApp-based registration and login for farmers
- Multilingual support (`hi`, `en`)
- Voice-based AI question answering using AgriVoice
- Produce listing and market price prediction via Agmarknet
- Weather forecasting using live location
- Order notifications for farmers

---

##  Tech Stack

- Python + Flask
- Meta WhatsApp Business API
- Integration with:
  - AgriVoice microservice (`/chat`)
  - AgriKart backend APIs (Farmer login, register, produce add)
  - Agmarknet scraper
  - OpenWeather API (via utility)
- Audio replies using gTTS

---

##  Setup Instructions

### Prerequisites

- Python 3.10+
- Flask
- `.env` file with:
  ```env
  VERIFY_TOKEN=your_webhook_verify_token
  ACCESS_TOKEN=your_meta_whatsapp_access_token
```