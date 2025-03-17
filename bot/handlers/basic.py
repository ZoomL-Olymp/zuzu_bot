import os
import pandas as pd
from aiogram import Router, types, F, Bot  # Добавлен Bot в импорт
from aiogram.filters import CommandStart
from aiogram.types import Message
from db.database import save_website_data, init_db
from utils import clean_price_string


router = Router()
TEMP_FILE_PATH = "data/temp_file.xlsx"

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}! 👋\n\n"
                         "Отправь мне Excel файл с данными о сайтах для парсинга.\n\n"
                         "Формат файла:\n"
                         "- Колонка 'title' - название сайта\n"
                         "- Колонка 'url' - ссылка на сайт\n"
                         "- Колонка 'xpath' - XPath к элементу с ценой")

@router.message(F.document)
async def handle_document(message: types.Message, bot: Bot): # Исправленная аннотация типа
    if message.document.file_name.endswith(('.xls', '.xlsx')):
        try:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, TEMP_FILE_PATH)

            df = pd.read_excel(TEMP_FILE_PATH)

            # Проверка наличия необходимых колонок
            required_columns = ['title', 'url', 'xpath']
            for col in required_columns:
                if col not in df.columns:
                    await message.answer(f"Ошибка: В файле отсутствует колонка '{col}'.")
                    os.remove(TEMP_FILE_PATH)
                    return

            # Вывод содержимого пользователю
            output_text = "Содержимое файла:\n\n"
            for index, row in df.iterrows():
                output_text += f"<b>{row['title']}</b>\n"
                output_text += f"URL: {row['url']}\n"
                output_text += f"XPath: {row['xpath']}\n\n"
            await message.answer(output_text, parse_mode="HTML")

            # Сохранение в БД
            websites_data = df.to_dict('records')
            save_website_data(websites_data)
            await message.answer("Данные сохранены в базу данных.")

            os.remove(TEMP_FILE_PATH)

        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {e}")
            if os.path.exists(TEMP_FILE_PATH):
                os.remove(TEMP_FILE_PATH)
    else:
        await message.answer("Пожалуйста, отправьте файл в формате Excel (.xls, .xlsx).")