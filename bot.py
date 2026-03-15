import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
counts = ["5", "10", "15", "20", "50"]
exp = ["Без опыта", "От 1 до 3 лет", "От 3 до 6 лет", "Более 6 лет"]
exp_map = {
    "Без опыта": "noExperience",
    "От 1 до 3 лет": "between1And3",
    "От 3 до 6 лет": "between3And6",
    "Более 6 лет": "moreThan6"
}
cities = {
    "москва": "1",
    "питер": "2",
    "новосибирск": "4",
    "екатеринбург": "3",
    "казань": "88"
}


user_data = {}

PAGE_SIZE = 5
def get_pagination_keyboard(page: int, total_pages: int):
    buttons=[]
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page_{page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
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
exp_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Без опыта"), KeyboardButton(text="От 1 до 3 лет")],
        [KeyboardButton(text="От 3 до 6 лет"), KeyboardButton(text="Более 6 лет")]
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
    user_data[user_id]["count"] = int(message.text)
    await message.answer("Укажите опыт работы",reply_markup=exp_keyboard)
@dp.message(F.text.in_(exp))
async def get_exp(message:types.Message):
    user_id = message.from_user.id
    experience = exp_map[message.text]
    count = user_data[user_id]["count"]
    keyword = user_data[user_id]["keyword"]
    area = user_data[user_id]["area"]

    url = f"https://api.hh.ru/vacancies?text={quote(keyword)}&area={area}&experience={experience}&search_field=name&per_page={count}"
   
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["items"]:
        await message.answer("Вакансий не найдено.Попробуйте ввести другое ключевое слово.")
        return
    
    user_data[user_id]["vacancies"] = data["items"]
    user_data[user_id]["page"] = 0
    await show_page(message,user_id)

async def show_page(message, user_id, edit = False):
    vacancies = user_data[user_id]["vacancies"]
    page = user_data[user_id]["page"]
    total_pages = (len(vacancies) + PAGE_SIZE - 1) // PAGE_SIZE

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_vacancies = vacancies[start:end]

    result = f"Страница {page + 1} из {total_pages}\n\n"
    for vacancy in page_vacancies:
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

    keyboard = get_pagination_keyboard(page, total_pages)
    if edit:
        await message.edit_text(result, parse_mode ="Markdown", reply_markup = keyboard)
    else:
        await message.answer(result, parse_mode = "Markdown", reply_markup = keyboard)
    

@dp.message()
async def ask_city(message: types.Message):
    if message.text.lower() in cities :
        await message.answer("Выберите город из кнопок ниже:", reply_markup=city_keyboard)
        return
    user_data[message.from_user.id] = {"keyword": message.text}
    await message.answer("Выберите город:", reply_markup=city_keyboard )
@dp.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery):
    user_id = callback.from_user.id
    page = int(callback.data.split("_")[1])
    user_data[user_id]["page"] = page
    await show_page(callback.message, user_id, edit= True)
    await callback.answer()
        
async def main():
    await dp.start_polling(bot)

asyncio.run(main())