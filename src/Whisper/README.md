#  AgriKart Transcription & Agri-QA Service

This is a FastAPI microservice that performs **automatic speech recognition** using OpenAI's Whisper model and generates **agriculture-specific answers** using a fine-tuned Flan-T5 model with LoRA. It powers the transcription and response pipeline in the AgriKart.ai voice assistant system.

---

##  Features

- Transcribes `.wav` audio using `openai/whisper-large-v3`
- Generates context-aware agri responses using `Flan-T5 + LoRA`
- Optimized for GPU but falls back to CPU if unavailable
- Accepts audio input via HTTP `POST`
- Lightweight and fast with streaming chunked inference

---

##  Model Stack

| Component          | Model Name                  |
|-------------------|-----------------------------|
| Transcription      | `openai/whisper-large-v3`   |
| LLM (base)         | `google/flan-t5-base`       |
| Fine-tuned weights | `LoRA` (at `./flan_t5_base_agri_lora_gpu`) |

---

##  Installation

### Prerequisites

- Python 3.10+
- Torch (`torch` with CUDA if available)
- FFmpeg (if preprocessing audio)
- GPU Recommended for fast inference

##  API Endpoint

### `POST /chat/`

Accepts an audio file in `.wav` format and returns the transcribed text along with an AI-generated agricultural answer.

---

###  Request (form-data)

| Field | Type       | Description          |
|-------|------------|----------------------|
| file  | UploadFile | Audio file (`.wav`)  |

---

### 🔹 Example cURL

```bash
curl -X POST http://localhost:8003/chat/ \
  -F "file=@sample_audio.wav"
```
##  Hardware Notes

 **GPU is required** to run this service efficiently.

- Uses `float16` precision on CUDA devices for faster inference
- Falls back to CPU (`float32`) only for testing; performance will degrade significantly
- Whisper is configured with `chunk_length_s=30` for handling long audio inputs efficiently
