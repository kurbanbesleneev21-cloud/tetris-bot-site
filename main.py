import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyrogram import Client, filters

# Стандартные публичные API-ключи Pyrogram
API_ID = int(os.environ.get("API_ID", 6))
API_HASH = os.environ.get("API_HASH", "eb06d4abfb49d3eeb1a350ac0c814d37")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOT = "gembot_tetris_bot"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tg_client = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
latest_data = {"text": "Ожидание сообщений от бота...", "buttons": []}

@tg_client.on_message(filters.chat(TARGET_BOT))
async def handle_msg(client, message):
    global latest_data
    buttons = []
    if message.reply_markup and message.reply_markup.inline_keyboard:
        for row in message.reply_markup.inline_keyboard:
            r = []
            for btn in row:
                r.append({"text": btn.text, "data": btn.callback_data})
            buttons.append(r)
            
    latest_data = {
        "text": message.text or message.caption or "Медиа",
        "buttons": buttons
    }

@app.post("/send")
async def send_cmd(cmd: str = "/start"):
    await tg_client.send_message(TARGET_BOT, cmd)
    await asyncio.sleep(2)
    return latest_data

@app.get("/get")
async def get_data():
    return latest_data

@app.on_event("startup")
async def startup():
    await tg_client.start()

@app.on_event("shutdown")
async def shutdown():
    await tg_client.stop()
