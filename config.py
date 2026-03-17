import os
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

TOKEN = os.getenv("TOKEN")

# Справочники
CITIES = {
    "москва": "1",
    "питер": "2",
    "новосибирск": "4",
    "екатеринбург": "3",
    "казань": "88"
}

EXP_MAP = {
    "Без опыта": "noExperience",
    "От 1 до 3 лет": "between1And3",
    "От 3 до 6 лет": "between3And6",
    "Более 6 лет": "moreThan6"
}

COUNTS = ["5", "10", "15", "20", "50"]
PAGE_SIZE = 5

# Клавиатуры
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