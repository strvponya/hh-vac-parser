import asyncio
import logging
import requests
from urllib.parse import quote
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

# Импортируем наше добро из других файлов
from config import TOKEN, CITIES, EXP_MAP, COUNTS, PAGE_SIZE, city_keyboard, number_keyboard, exp_keyboard
from utils import get_pagination_keyboard, format_vacancy_text

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет! Напиши ключевое слово для поиска (например: Python)")

@dp.message(F.text.lower().in_(CITIES.keys()))
async def choose_counts(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data: return
    user_data[uid]["area"] = CITIES[message.text.lower()]
    await message.answer("Сколько вакансий показать?", reply_markup=number_keyboard)

@dp.message(F.text.in_(COUNTS))
async def choose_exp(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data: return
    user_data[uid]["count"] = int(message.text)
    await message.answer("Укажите опыт работы", reply_markup=exp_keyboard)

@dp.message(F.text.in_(EXP_MAP.keys()))
async def get_results(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data: return
    
    data = user_data[uid]
    experience = EXP_MAP[message.text]
    
    url = f"https://api.hh.ru/vacancies?text={quote(data['keyword'])}&area={data['area']}&experience={experience}&search_field=name&per_page={data['count']}"
    headers = {"User-Agent": "JobSearchBot/1.0"}
    
    await message.answer("⏳ Загружаю вакансии...", reply_markup=ReplyKeyboardRemove())
    
    try:
        response = requests.get(url, headers=headers)
        res_data = response.json()
        if not res_data.get("items"):
            await message.answer("Ничего не найдено.")
            return
        
        user_data[uid]["vacancies"] = res_data["items"]
        user_data[uid]["page"] = 0
        await show_page(message, uid)
    except Exception as e:
        await message.answer("Ошибка связи с HH.ru")

async def show_page(message, user_id, edit=False):
    data = user_data[user_id]
    vacs = data["vacancies"]
    page = data["page"]
    
    total_pages = (len(vacs) + PAGE_SIZE - 1) // PAGE_SIZE
    start = page * PAGE_SIZE
    page_items = vacs[start : start + PAGE_SIZE]

    text = f"📄 Страница {page + 1} из {total_pages}\n\n"
    for v in page_items:
        text += format_vacancy_text(v)

    kb = get_pagination_keyboard(page, total_pages)
    if edit:
        await message.edit_text(text, parse_mode="Markdown", reply_markup=kb, disable_web_page_preview=True)
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=kb, disable_web_page_preview=True)

@dp.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data: return
    user_data[uid]["page"] = int(callback.data.split("_")[1])
    await show_page(callback.message, uid, edit=True)
    await callback.answer()

@dp.message()
async def save_keyword(message: types.Message):
    user_data[message.from_user.id] = {"keyword": message.text}
    await message.answer("Выберите город:", reply_markup=city_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())