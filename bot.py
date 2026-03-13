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
counts = ["5", "10", "15", "20", "50"]
cities = {
    "москва": "1",
    "питер": "2",
    "новосибирск": "4",
    "екатеринбург": "3",
    "казань": "88"
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
number_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="5"), KeyboardButton(text="10")],
        [KeyboardButton(text="15"), KeyboardButton(text="20")],
        [KeyboardButton(text="50")]
    ],
    resize_keyboard=True  
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Напиши ключевое слово для поиска вакансий")

@dp.message(Command("help"))
async def help_сommand(message: types.Message):
    await message.answer("Данный бот позволяет найти нужную вакансию на hh.ru. Для этого вам нужно ввести команду /start, ввести ключевое слово (Например: Python) и выбрать нужный город")

@dp.message(F.text.lower().in_(cities.keys()))
async def choose_counts(message:types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Сначала введи ключевое слово для поиска")
        return
    user_data[user_id]["area"] = cities[message.text.lower()]
    await message.answer("Сколько вакансий показать?",reply_markup=number_keyboard)
@dp.message(F.text.in_(counts))
async def get_vacancies(message:types.Message):
    user_id = message.from_user.id
    count = int(message.text)
    keyword = user_data[user_id]["keyword"]
    area = user_data[user_id]["area"]


    
    url = f"https://api.hh.ru/vacancies?text={quote(keyword)}&area={area}&search_field=name"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["items"]:
        await message.answer("Вакансий не найдено.Попробуйте ввести другое ключевое слово.")
        return
    
    result = ""
    for vacancy in data["items"][:count]:
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
    if message.text.lower() in cities :
        await message.answer("Выберите город из кнопок ниже:", reply_markup=city_keyboard)
        return
    user_data[message.from_user.id] = {"keyword": message.text}
    await message.answer("Выберите город:", reply_markup=city_keyboard )

        
async def main():
    await dp.start_polling(bot)

asyncio.run(main())