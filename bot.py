import logging
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# Беремо токен з налаштувань Render
API_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def run_piston_code(code):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {"language": "python", "version": "3.10.0", "files": [{"content": code}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get('run', {}).get('output', 'Помилка виконання')
    except:
        return "Помилка зв'язку з сервером коду."

@dp.message(Command("py"))
async def execute_py(message: types.Message):
    # Витягуємо код після команди /py
    code = message.text[4:].strip() 
    if not code:
        await message.reply("Напиши код, наприклад: /py print(123)")
        return
    res = run_piston_code(code)
    await message.answer(f"🐍 **Результат:**\n```python\n{res}\n```", parse_mode="Markdown")

# Функція "анти-вимкнення" для Render
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Бот живий!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    # Запускаємо веб-сервер фоном, щоб Render не закрив сервіс
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
