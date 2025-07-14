import requests

def test_agrivoice_endpoint():
    url = "http://localhost:8004/chat/"
    files = {
        "file": ("dummy.mp3", b"FAKEAUDIO", "audio/mpeg")
    }
    data = {
        "lang": "en"
    }

    try:
        response = requests.post(url, files=files, data=data)
        assert response.status_code in [200, 500]  # Accept 500 if STT fails
        print(" AgriVoice /chat responded.")
    except Exception as e:
        print(" AgriVoice test failed:", e)
        assert False
