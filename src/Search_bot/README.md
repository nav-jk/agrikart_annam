#  Search Bot – Google CSE Wrapper for AgriKart.ai

The Search Bot is a FastAPI-based microservice that wraps Google Custom Search Engine (CSE) to return concise web snippets relevant to agricultural queries. It is designed to support AgriKart.ai's voice assistant by providing context-aware search results.

---

##  Features

- Accepts search queries via POST request
- Uses Google CSE to fetch top results
- Extracts and returns only text snippets
- Configurable number of results
- Async, lightweight, and fast

---

##  Tech Stack

- FastAPI
- httpx (async HTTP client)
- Google Custom Search API
- Pydantic for request validation
- dotenv for environment configuration

---

##  Installation

### Prerequisites

- Python 3.10+
- Google CSE API Key and CSE ID
- `.env` file with:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

##  API

### `POST /search/`

Send a query and receive relevant snippets from the web.

####  Request Body

```json
{
  "query": "organic fertilizer for tomato plants",
  "num_results": 5
}
```

####  Response
```json
{
  "snippets": [
    "Use compost or well-rotted manure to enhance soil fertility...",
    "Neem cake is a popular organic option for pest control in tomato fields...",
    "..."
  ]
}
```