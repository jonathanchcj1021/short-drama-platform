"""FastAPI 應用程式入口。"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, categories, cms, dramas, episodes, google_auth

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Short Drama Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案（示例影片等）
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(google_auth.router)
app.include_router(categories.router)
app.include_router(dramas.router)
app.include_router(episodes.router)
app.include_router(cms.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
