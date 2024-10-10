from fastapi import FastAPI
from routes import rss_feed
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include the rss-feed router
app.include_router(rss_feed.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
