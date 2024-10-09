import os
from fastapi import APIRouter
import json
import httpx
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Create a router instance
router = APIRouter()

NYT_LIVE_FEED_BASE_URL = os.getenv("NYT_LIVE_FEED_BASE_URL")
CNN_LIVE_FEED_BASE_URL = os.getenv("CNN_LIVE_FEED_BASE_URL")
FOX_NEWS_LIVE_FEED_BASE_URL = os.getenv("FOX_NEWS_LIVE_FEED_BASE_URL")
FEDERAL_REG_LIVE_FEED_BASE_URL = os.getenv("FEDERAL_REG_LIVE_FEED_BASE_URL")

url_list = [
    NYT_LIVE_FEED_BASE_URL,
    CNN_LIVE_FEED_BASE_URL,
    FOX_NEWS_LIVE_FEED_BASE_URL,
    FEDERAL_REG_LIVE_FEED_BASE_URL
]

async def get_cnn_live_feed():
    parsed_items = []
    for url in url_list:
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Failed to fetch RSS feed"}
        # Parse the XML data using BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')
        # Print the title and link of each item
        items = soup.find_all('item')
        for item in items:
            title = item.title.text
            link = item.guid.text
            description = item.description.text
            parsed_items.append({"title": title, "link": link, "description": description})
    # Return the response from the external API
    return parsed_items

# Define the rss-feed route
@router.get("/rss-feed")
async def get_rss_feed():
    cnn_live_feed_list = await get_cnn_live_feed()
    return { "data": cnn_live_feed_list }
