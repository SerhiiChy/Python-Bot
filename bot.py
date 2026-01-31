import os
import logging
import requests
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import asyncio

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + f"/webhook/{API_TOKEN}"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

def run_piston_code(code):
    try:
        r = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language": "python", "version": "3.10.0", "files": [{"content": code}]},
            timeout=10
        )
        return r.json().get("run", {}).get("output", "Помилка виконання")
    except:
        return "Помилка з'єднання з сервером."

@dp.message_handler(commands=["py"])
async def execute_py(message: types.Message):
    code = message.get_args()
    if not code:
        await message.reply("Приклад: /py print(123)")
        return
    result = run_piston_code(code)
    await message.answer(f"```python\n{result}\n```", parse_mode="Markdown")

@app.route("/", methods=["GET"])
def index():
    return "OK"

@app.route(f"/webhook/{API_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update(**request.json)
    asyncio.create_task(dp.process_update(update))
    return "OK"

if __name__ == "__main__":
    # Регистрация webhook
    asyncio.get_event_loop().run_until_complete(bot.set_webhook(WEBHOOK_URL))
    # Flask запускает HTTP-сервер на порту, который видит Render
    app.run(host="0.0.0.0", port=PORT)
