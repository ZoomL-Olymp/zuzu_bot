import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения из файла .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    print("Ошибка: Не найден BOT_TOKEN в файле .env")
    exit(1) # Или можно поднять исключение, в зависимости от того, как вы хотите обрабатывать ошибки