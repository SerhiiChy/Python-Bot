import os
import logging
import requests
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import asyncio

API_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)


def run_piston_code(code):
    try:
        r = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={
                "language": "python",
                "version": "3.10.0",
                "files": [{"content": code}],
            },
            timeout=10,
        )
        return r.json().get("run", {}).get("output", "Помилка виконання")
    except:
        return "Помилка звʼязку з сервером."


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
    return "OK", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update(**request.json)
    asyncio.run(dp.process_update(update))
    return "OK", 200


if __name__ == "__main__":
    asyncio.run(bot.set_webhook(WEBHOOK_URL))
    app.run(host="0.0.0.0", port=PORT)
