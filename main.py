from fastapi import FastAPI, WebSocket
import asyncio
from database import get_rss_feed_collection
from routes import rss_feed
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from utils.rss_data import get_realtime_rss_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

gettingRealtimeRSSFeed = False

async def get_rss_feed_middleware():
    global gettingRealtimeRSSFeed
    try:
        await get_realtime_rss_data()
    finally:
        # Ensure the flag is reset to False after fetching completes
        gettingRealtimeRSSFeed = False

class RSSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        global gettingRealtimeRSSFeed
        if gettingRealtimeRSSFeed:
            return await call_next(request)
        gettingRealtimeRSSFeed = True
        asyncio.create_task(get_rss_feed_middleware())

        response = await call_next(request)
        return response

app.add_middleware(RSSMiddleware)

# Include the rss-feed router
app.include_router(rss_feed.router)

# WebSocket connection to stream updates
@app.get("/realtime-rss-feed")
async def rss_feed_endpoint(websocket: WebSocket):
    previous_data = []
    rss_feed_collection=get_rss_feed_collection()
    while True:
        current_data = list(rss_feed_collection.find().sort("pub_date", -1).limit(10))
        if current_data != previous_data:
            previous_data = current_data
            await websocket.send_json(current_data)
        await asyncio.sleep(10)  # Check for updates every 10 seconds

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
