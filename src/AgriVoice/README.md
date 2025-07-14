# AgriVoice – Voice Assistant for Farmers

AgriVoice is a FastAPI microservice in the AgriKart.ai platform that allows farmers to ask agricultural questions using voice and receive spoken answers in their native languages.

## Features

- Accepts `.mp3` or `.ogg` audio uploads
- Transcribes speech using external Whisper API
- Refines noisy input using DeepSeek LLM
- Searches TNAU agricultural knowledge base
- Responds with a simple voice reply using gTTS

## Setup

### Prerequisites

- Python 3.11
- FFmpeg
- `.env` file with API keys:
  ```env
  GOOGLE_API_KEY=your_google_key
  GOOGLE_CSE_ID=your_cse_id
  OPENROUTER_API_KEY=your_openrouter_key

## API

### `POST /chat/`

Upload an audio file and language code.

**Form fields:**

- `file`: audio file (`.ogg` or `.mp3`)
- `lang`: language code (e.g., `hi`, `ta`, `en`)

**Response:**

```json
{
  "language": "hi",
  "transcription": "Neem oil ke istemal kaise karein?",
  "response": "Neem tel 5 ml per liter paani mein milakar subah chhidkaav karein.",
  "audio_url": "http://localhost:8004/static/audio/..."
}
