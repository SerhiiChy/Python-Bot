import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

# Беремо токен із налаштувань сервера (безпека!)
API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def run_piston_code(code):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python",
        "version": "3.10.0",
        "files": [{"content": code}]
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        output = response.json().get('run', {}).get('output', 'Помилка виконання')
        return output if output else "Код виконаний успішно (без виводу)."
    except:
        return "Помилка зв'язку з сервером виконання."

@dp.message_handler(commands=['py'])
async def execute_py(message: types.Message):
    code = message.get_args()
    if not code:
        await message.reply("Напишіть код після команди. Приклад: `/py print(123)`")
        return
    
    result = run_piston_code(code)
    # Форматуємо відповідь у блок коду
    await message.answer(f"🐍 **Результат:**\n```python\n{result}\n```", parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
