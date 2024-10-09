from fastapi import FastAPI
from routes import rss_feed

app = FastAPI()

# Include the rss-feed router
app.include_router(rss_feed.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
