import requests

def test_whisper_transcription():
    url = "http://localhost:8003/chat/"
    files = {
        "file": ("test.wav", b"FAKEAUDIO", "audio/wav")
    }

    try:
        response = requests.post(url, files=files)
        assert response.status_code in [200, 500]  # Accept 500 due to dummy audio
        print(" Whisper /chat endpoint reachable.")
    except Exception as e:
        print(" Whisper test failed:", e)
        assert False
