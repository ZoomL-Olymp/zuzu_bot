import sqlite_utils

DATABASE_NAME = "data/zuzu_bot.db" # Путь к файлу БД

def init_db():
    """Создает базу данных и таблицу, если их нет."""
    db = sqlite_utils.Database(DATABASE_NAME)
    db.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        )
    """)

def save_website_data(websites_data):
    """Сохраняет данные о сайтах в базу данных."""
    db = sqlite_utils.Database(DATABASE_NAME)
    table = db["websites"]
    table.insert_all(websites_data, pk="id") # pk="id" чтобы избежать ошибок, если id уже существует (в данном случае не должно, но на всякий случай)

def get_all_websites():
    """Возвращает все сайты из базы данных."""
    db = sqlite_utils.Database(DATABASE_NAME)
    return list(db.query("SELECT id, title, url, xpath FROM websites"))

# Инициализация БД при импорте модуля (можно и в main.py при запуске)
init_db()