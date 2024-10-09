import os
from fastapi import APIRouter
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a router instance
router = APIRouter()

NYT_LIVE_FEED_BASE_URL = os.getenv("NYT_LIVE_FEED_BASE_URL")
NYT_API_KEY = os.getenv("NYT_API_KEY")


async def get_new_york_time_live_feed():
    url = f"{NYT_LIVE_FEED_BASE_URL}?api-key={NYT_API_KEY}"

    # Asynchronous HTTP GET request using httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    extracted_data = []

    realtimeFeed = response.json()
    print(realtimeFeed["results"])
    for result in realtimeFeed["results"]:
        title = result.get("title", "No title found")
        abstract = result.get("abstract", "No abstract found")
        source = result.get("source", "No source found")
        extracted_data.append({"title": title, "abstract": abstract, "source": source})

    # Return the response from the external API
    return {"status_code": response.status_code, "data": extracted_data}

# Define the rss-feed route
@router.get("/rss-feed")
async def get_rss_feed():
    new_york_time_live_feed = await get_new_york_time_live_feed()
    return new_york_time_live_feed
