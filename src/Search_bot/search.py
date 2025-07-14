import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

print(" GOOGLE_API_KEY Loaded:", bool(GOOGLE_API_KEY))
print(" GOOGLE_CSE_ID Loaded:", bool(GOOGLE_CSE_ID))

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    num_results: int = 10

@app.post("/search/")
async def search_handler(request: SearchRequest):
    query = request.query
    max_results = request.num_results

    print(f"\n Received Search Request: query='{query}', num_results={max_results}")

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": max_results
    }

    print(" Request Params:", params)
    print(" Making GET request to:", search_url)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(search_url, params=params)
            print(f"📡 Response Status Code: {res.status_code}")
            print("📦 Raw Response Text:", res.text[:1000])  # Truncate to avoid overflow

            res.raise_for_status()

            data = res.json()
            print(" JSON Loaded")

            if "items" not in data:
                print(" No 'items' in response! Full JSON:", data)

            snippets = [item.get("snippet", "") for item in data.get("items", [])]
            print(" Extracted Snippets:", snippets)
            return {"snippets": snippets}

    except Exception as e:
        print(" TNAU Search Error:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
