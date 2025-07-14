# AgriKart.ai: Voice-Driven E-Commerce for Indian Farmers

AgriKart.ai is a revolutionary e-commerce platform that enables Indian farmers to **list and sell their produce using just a WhatsApp voice message**. Built with voice-first technology and powered by AI, it connects farmers and buyers across the nation, even those without literacy skills.

---

##  Why AgriKart?

- **No apps. No typing. Just voice.**
- **WhatsApp-based onboarding** for farmers
- **Voice-to-Voice AI assistant** answers agri-related queries in native languages
- **Seamless produce listing**, discovery, and communication between farmers and buyers

---

##  Project Structure

This monorepo contains all services that make AgriKart.ai work:

```bash
.
├── src/
│   ├── agrivoice/        # Voice-to-voice AI assistant using FastAPI + DeepSeek + gTTS
│   ├── whisper/          # Audio transcription 
│   ├── search_bot/       # Google CSE wrapper for farming context
│   ├── backend/          # Django backend (JWT auth, produce listings, users)
│   └── frontend/         # React dashboard for admin/buyers
│   └── whatsapp_bot/     
├── notebooks/            
├── tests/                
├── docs/
│   ├── architecture.png  # System architecture diagram
│   └── cards/
│       ├── project-card.ipynb
│       └── ml-metrics.json
├── docker-compose.yml
├── logs.txt              # Docker + API logs
├── transcript.txt        
└── README.md         
```    

##  Setup Instructions

### Prerequisites

- Docker + Docker Compose  
- Python 3.11  
- Node.js 20+  
- `.env` files in each service folder (see below)

---

### Run Everything (Development)

```bash
docker-compose up --build
```

##  .env Setup

### `AgriVoice/.env`

```env
GOOGLE_API_KEY=your_google_key
GOOGLE_CSE_ID=your_cse_id
OPENROUTER_API_KEY=your_openrouter_key
```

### `Search_bot/.env`
```env
GOOGLE_API_KEY=your_google_key
GOOGLE_CSE_ID=your_cse_id
```

### `Backend/.env`
```env
SECRET_KEY=your_django_secret
DEBUG=True
DB_PATH=/data/db.sqlite3
```

### `WhatsApp_bot/.env`
```env
WHATSAPP_TOKEN=...
VERIFY_TOKEN=...
WHATSAPP_PHONE_ID=...
```

##  Project-Level READMEs

Each subcomponent of AgriKart.ai is modularized and documented individually:

<<<<<<< HEAD
- [AgriVoice README](src/agrivoice/README.md)
- [Whisper README](src/whisper/README.md)
- [Search Bot README](src/search_bot/README.md)
- [Backend (Django) README](src/backend/README.md)
- [Frontend (React) README](src/frontend/README.md)
- [WhatsApp Bot README](src/whatsapp_bot/README.md)

##  Real-World Deployment Constraints

While the project runs as microservices, some components require setup that can't be easily containerized or documented in a simple README:

---

###  WhatsApp Bot Requires:

- A **commercial Facebook account**
- **Verified Meta Business profile**
- **Approved phone number** via WhatsApp Business API

These steps involve human verification and cannot be scripted or demoed locally.

---

###  Whisper Transcription Service:

- Requires a **GPU-enabled environment with CUDA support**
- Not feasible to run locally on CPU due to performance constraints
- Whisper models demand significant VRAM; they are **intended for cloud deployment only**

---

Due to these limitations, we've hosted a working version of the platform for demonstration and testing:

 **Live Demo**:  
[https://agrikart-fd-ws-2a-80.ml.iit-ropar.truefoundry.cloud/](https://agrikart-fd-ws-2a-80.ml.iit-ropar.truefoundry.cloud/)
=======
- [AgriVoice README](src/AgriVoice/README.md)
- [Whisper README](src/Whisper/README.md)
- [Search Bot README](src/Search_bot/README.md)
- [Backend (Django) README](src/Backend/README.md)
- [Frontend (React) README](src/Frontend/README.md)
- [WhatsApp Bot README](src/WhatsApp_bot/README.md)
>>>>>>> 7b90a15569f5d6e26697cc83f4be7c0c0cda30eb
