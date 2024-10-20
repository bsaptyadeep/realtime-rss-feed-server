import os
from fastapi import APIRouter
import json
from openai import OpenAI
import httpx
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

from database import get_rss_feed_collection

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
async def classify_news_array(paragraphs: list[str]) -> list[str]:
    """
    Classifies an array of news paragraphs into categories:
    Politics, War, Finance, Technology, Health, Entertainment.
    
    Args:
        paragraphs (list[str]): A list of news paragraphs to classify.
    
    Returns:
        list[str]: A list of predicted categories for each paragraph.
    """
    # Define the categories
    categories = ["Politics", "War", "Finance", "Technology", "Health", "Entertainment"]
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPEN_AI_API_KEY")
    )
    
    messages = [
        {"role": "system", "content": "You are an expert news classifier."},
        {"role": "user", "content": f"Classify the following news paragraphs into one of the categories: {', '.join(categories)}."}
    ]
    
    # Append each paragraph to the user message
    for i, paragraph in enumerate(paragraphs):
        messages.append({"role": "user", "content": f"Paragraph {i+1}: {paragraph}"})
    
    # Add a final request for a list of categories
    messages.append({"role": "user", "content": "Return a list of categories, one for each paragraph, in the same order."})


    # Call the OpenAI Chat API (for models like gpt-3.5-turbo or gpt-4)
    response = client.chat.completions.create(
        model="gpt-4",  # Use 'gpt-3.5-turbo' if gpt-4 is unavailable
        messages=messages,
        max_tokens=10*len(paragraphs),
        temperature=0  # Set temperature to 0 for deterministic results
    )

    print("testing rss", response.choices[0].message)
    # Return the category if it's valid, otherwise return 'Unknown'
    return ""
# Example usage:
news_paragraphs = [
    "The stock market experienced a significant decline today, with major indexes losing over 2% in value.",
    "New tech innovations in AI are transforming the healthcare industry, providing better patient outcomes.",
    "The president announced a new policy to address international trade agreements."
]

async def get_category_list(arr):
    # Check if the array can be divided into equal chunks of 10
    l = len(arr)
    if (l-(l%10)) % 10 != 0:
        print("Array size is not divisible by 10.")
        return []

    # Dividing the array into chunks of size 10
    batches = [arr[i:i + 10] for i in range(0, len(arr), 10)]
    batches.append(arr[l-(l%10):l])
    for i, batch in enumerate(batches):
        categories = await classify_news_array(batch)
        print(f"batch {i+1} processed ---")
    # return result

# categories = classify_news_array(news_paragraphs)
# print(f"The categories of the news are: {categories}")
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
        titles = [];
        for item in items:
            title = item.title.text
            link = item.guid.text
            description = item.description.text
            titles.append(title)
            if title:
                titles.append(title)
                parsed_items.append({"title": title, "link": link, "description": description})
    await get_category_list(titles)
    print(len(parsed_items))

    # Return the response from the external API
    return parsed_items

# Define the rss-feed route
@router.get("/rss-feed")
async def get_rss_feed():
    rss_feed_collection=get_rss_feed_collection()
    current_data = await rss_feed_collection.find({}).to_list(None)
    res_current_list = []
    for item in current_data:
        item["_id"] = str(item["_id"])
        item["title"] = str(item["title"])
        item["link"] = str(item["link"])
        item["description"] = str(item["description"])
        item["category"] = str(item["category"])
        res_current_list.append(item)
    return { "data": current_data }
