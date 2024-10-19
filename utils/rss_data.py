from bs4 import BeautifulSoup
import requests
import os
from openai import OpenAI
import re
from database import get_rss_feed_collection

NYT_LIVE_FEED_BASE_URL = os.getenv("NYT_LIVE_FEED_BASE_URL")
CNN_LIVE_FEED_BASE_URL = os.getenv("CNN_LIVE_FEED_BASE_URL")
FOX_NEWS_LIVE_FEED_BASE_URL = os.getenv("FOX_NEWS_LIVE_FEED_BASE_URL")
FEDERAL_REG_LIVE_FEED_BASE_URL = os.getenv("FEDERAL_REG_LIVE_FEED_BASE_URL")
BATCH_SIZE = 20

url_list = [
    NYT_LIVE_FEED_BASE_URL,
    CNN_LIVE_FEED_BASE_URL,
    FOX_NEWS_LIVE_FEED_BASE_URL,
    FEDERAL_REG_LIVE_FEED_BASE_URL
]

def extract_words(input_string):
    # Use regex to remove numbers, periods, and excess whitespace
    cleaned_string = re.sub(r'[^a-zA-Z\s]', '', input_string).strip()
    # Split the cleaned string by line or any other form of separation
    words_list = cleaned_string.splitlines()
    # Filter empty strings
    return [word.strip() for word in words_list if word.strip()]

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
        {"role": "user", "content": f"Individually classify each of the following news paragraphs into one of the categories: {', '.join(categories)}. Please avoid classifying all paragraphs under a single category unless they clearly belong to that category. Instead, return a formatted list indicating the category for each paragraph in the following format:\n1. Category\n2. Category\n3. Category\n... and so on."}
    ]
    # Append each paragraph to the user message
    for i, paragraph in enumerate(paragraphs):
        messages.append({"role": "user", "content": f"Paragraph {i+1}: {paragraph}"})
    # Add a final request for a list of categories
    messages.append({"role": "user", "content": "Return a list of categories, one for each paragraph, in the specified format."})

    # Call the OpenAI Chat API (for models like gpt-3.5-turbo or gpt-4)
    response = client.chat.completions.create(
        model="gpt-4",  # Use 'gpt-3.5-turbo' if gpt-4 is unavailable
        messages=messages,
        max_tokens=10*BATCH_SIZE,
        temperature=0  # Set temperature to 0 for deterministic results
    )
    # Return the category if it's valid, otherwise return 'Unknown'
    category_list = extract_words(response.choices[0].message.content)
    return category_list


def get_batches_from_list(arr):
    l = len(arr)
    # Dividing the array into chunks of size 10
    batches=[]
    if l>BATCH_SIZE:
        batches = [arr[i:i + BATCH_SIZE] for i in range(0, len(arr), BATCH_SIZE)]
    batches.append(arr[l-(l%BATCH_SIZE):l])
    return batches

async def get_realtime_rss_data():
    parsed_items = []
    rss_feed_collection = get_rss_feed_collection()
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
            if await rss_feed_collection.find_one({"link": link}) is None and title:
                parsed_items.append({"title": title, "link": link, "description": description})
    print("testing~realtime", parsed_items)
    if len(parsed_items) == 0:
        return;

    items_batches = get_batches_from_list(parsed_items)
    rss_feed_list = [];
    for batch in items_batches:
        titles = []
        for item in batch:
            titles.append(item["title"])
        category_list = await classify_news_array(titles)
        for i in range(0, len(category_list)):
            rss_feed_list.append({
                "title": batch[i]["title"],
                "link": batch[i]["link"],
                "description": batch[i]["description"],
                "category": category_list[i]
                })
    if len(rss_feed_list) > 0:
        await rss_feed_collection.insert_many(rss_feed_list)
    # Return the response from the external API
    return;