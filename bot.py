import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from urllib.parse import quote

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

cities = {
    "Москва": "1",
    "Питер": "2",
    "Новосибирск": "4",
    "Екатеринбург": "3",
    "Казань": "88"
}


user_data = {}


city_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Москва"), KeyboardButton(text="Питер")],
        [KeyboardButton(text="Новосибирск"), KeyboardButton(text="Екатеринбург")],
        [KeyboardButton(text="Казань")]
    ],
    resize_keyboard=True  
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Напиши ключевое слово для поиска вакансий")

@dp.message(F.text.in_(cities.keys()))
async def get_vacancies(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Сначала введи ключевое слово для поиска")
        return
    
    keyword = user_data[user_id]
    area = cities[message.text]
    
    url = f"https://api.hh.ru/vacancies?text={quote(keyword)}&area={area}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    result = ""
    for vacancy in data["items"][:5]:
        name = vacancy["name"]
        link = vacancy["alternate_url"]
        salary = vacancy["salary"]
        
        if salary:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = salary.get("currency", "")
            if salary_from and salary_to:
                sal_str = f"от {salary_from} до {salary_to} {currency}"
            elif salary_from:
                sal_str = f"от {salary_from} {currency}"
            elif salary_to:
                sal_str = f"до {salary_to} {currency}"
            else:
                sal_str = "не указана"
        else:
            sal_str = "не указана"
        
        result += f"*{name}*\n{sal_str}\n{link}\n\n"
    
    await message.answer(result, parse_mode="Markdown")

@dp.message()
async def ask_city(message: types.Message):
    user_data[message.from_user.id] = message.text
    await message.answer("Выбери город:", reply_markup=city_keyboard)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())