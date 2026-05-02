import asyncio
import logging
import os
from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot.config import get_settings
from bot.main import run_bot, stop_bot as aiogram_stop_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state to keep track of the bot task
bot_task: asyncio.Task | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # On shutdown, ensure the bot task is cancelled
    global bot_task
    if bot_task and not bot_task.done():
        bot_task.cancel()
        try:
            await asyncio.wait_for(bot_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

app = FastAPI(lifespan=lifespan)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    if not os.path.exists("static/index.html"):
        raise HTTPException(status_code=404, detail="Dashboard UI not found")
    return FileResponse("static/index.html")

@app.get("/api/bot/status")
async def get_bot_status():
    global bot_task
    is_running = bot_task is not None and not bot_task.done()
    return {"running": is_running}

@app.post("/api/bot/start")
async def start_bot():
    global bot_task
    if bot_task and not bot_task.done():
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    # Clear settings cache so it picks up any new .env values
    get_settings.cache_clear()
    
    bot_task = asyncio.create_task(run_bot())
    logger.info("Bot background task started via web API.")
    return {"status": "started"}

@app.post("/api/bot/stop")
async def stop_bot():
    global bot_task
    if not bot_task or bot_task.done():
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    await aiogram_stop_bot()
    logger.info("Bot polling stopped via web API.")
    return {"status": "stopped"}

@app.get("/api/settings")
async def get_env_settings():
    # Read directly from .env file to show what's saved
    env_vars = dotenv.dotenv_values(".env")
    return {"settings": env_vars}

class SettingsUpdate(BaseModel):
    settings: dict[str, str]

@app.post("/api/settings")
async def update_env_settings(data: SettingsUpdate):
    try:
        # Update each key in the .env file
        for key, value in data.settings.items():
            # If the user sends an empty string, we can still save it or handle it.
            # python-dotenv handles this gracefully.
            dotenv.set_key(".env", key, value)
        
        # Clear the runtime cache so next start picks up new values
        get_settings.cache_clear()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
