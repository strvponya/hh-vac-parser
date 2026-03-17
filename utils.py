from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_pagination_keyboard(page: int, total_pages: int):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page_{page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def format_vacancy_text(vacancy):
    name = vacancy["name"]
    link = vacancy["alternate_url"]
    salary = vacancy.get("salary")
    
    if salary:
        s_from = f"от {salary['from']}" if salary.get('from') else ""
        s_to = f"до {salary['to']}" if salary.get('to') else ""
        currency = salary.get('currency', '')
        sal_str = f"{s_from} {s_to} {currency}".strip()
    else:
        sal_str = "не указана"
        
    return f"🔹 *{name}*\n💰 З/П: {sal_str}\n🔗 [Открыть на HH]({link})\n\n"