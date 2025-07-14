import requests

def test_search_api():
    url = "http://localhost:8002/search/"
    payload = {
        "query": "best fertilizer for tomato",
        "num_results": 3
    }

    try:
        response = requests.post(url, json=payload)
        assert response.status_code == 200
        assert "snippets" in response.json()
        print(" Search bot returned snippets.")
    except Exception as e:
        print(" Search bot test failed:", e)
        assert False
