import os
import logging
import requests
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import asyncio

# Настройки
API_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # https://python-bot-8xou.onrender.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# --- Выполнение кода через Piston ---
def run_piston_code(code):
    try:
        r = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language": "python", "version": "3.10.0", "files": [{"content": code}]},
            timeout=10
        )
        return r.json().get("run", {}).get("output", "Помилка виконання")
    except Exception as e:
        return f"Помилка API: {e}"

# --- Обработчик команды /py ---
@dp.message_handler(commands=["py"])
async def execute_py(message: types.Message):
    code = message.get_args()
    if not code:
        await message.reply("Напиши код после /py, например: `/py print(2+2)`")
        return
    result = run_piston_code(code)
    await message.answer(f"```python\n{result}\n```", parse_mode="Markdown")

# --- Мини-сервер для Render ---
@app.route("/", methods=["GET"])
def index():
    return "OK"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update(**request.json)
    asyncio.create_task(dp.process_update(update))
    return "OK"

# --- Старт ---
if __name__ == "__main__":
    # Регистрация webhook
    asyncio.get_event_loop().run_until_complete(bot.set_webhook(WEBHOOK_URL))
    # Flask реально открывает порт для Render
    app.run(host="0.0.0.0", port=PORT)
