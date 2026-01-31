import os
import logging
import requests
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.utils.executor import start_webhook

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)


def run_piston_code(code):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python",
        "version": "3.10.0",
        "files": [{"content": code}]
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("run", {}).get("output", "Помилка виконання")
    except:
        return "Помилка з'єднання з сервером виконання."


@dp.message_handler(commands=["py"])
async def execute_py(message: types.Message):
    code = message.get_args()
    if not code:
        await message.reply("Напишіть код після команди: /py print(123)")
        return

    result = run_piston_code(code)
    await message.answer(
        f"Результат:\n```python\n{result}\n```",
        parse_mode="Markdown"
    )


@app.route("/", methods=["GET"])
def healthcheck():
    return "OK", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
async def telegram_webhook():
    update = Update(**request.json)
    await dp.process_update(update)
    return "OK", 200


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    await bot.delete_webhook()


if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=PORT,
    )
