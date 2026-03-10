import requests
from urllib.parse import quote


results = []
keyword = input("Введи ключевое слово: ")
city = input("Введи город (москва/питер/новосибирск/екатеринбург/казань): ").lower()

cities = {
    "москва": "1",
    "питер": "2",
    "новосибирск": "4",
    "екатеринбург": "3",
    "казань": "88"
}

area = cities.get(city, "1")

# обращаемся к официальному API hh.ru вместо парсинга HTML
url = f"https://api.hh.ru/vacancies?text={quote(keyword)}&area={area}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
}

response = requests.get(url, headers=headers)

# .json() - превращает ответ сервера из текста в словарь Python
data = response.json()

# data["items"] - список вакансий внутри ответа
for vacancy in data["items"]:
    name = vacancy["name"]
    if not name:
        continue
    link = vacancy["alternate_url"]
    
    # зарплата может отсутствовать - проверяем через if
    salary = vacancy["salary"]
    if salary:
        salary_from = salary.get("from", "не указано")
        salary_to = salary.get("to", "не указано")
        currency = salary.get("currency", "")
        if salary_from and salary_to:
            sal_str = f" от {salary_from} до {salary_to} {currency}"
        elif salary_from: 
            sal_str = f"от {salary_from} {currency}"
        elif salary_from:
            sal_str = f"до {salary_to} {currency}"
    else:
        sal_str = "не указана"
    print(f"{name} | {sal_str}")
    print(link)
    print("---")
    results.append(f"{name} | {sal_str}\n{link}\n---\n")
with open("vacancies.txt", "w", encoding ="utf-8") as f:
    f.writelines(results)
print(f"\nСохранено {len(results)} вакансий в vacancies.txt")