import os
import pandas as pd
import sqlite3
from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from db.database import save_website_data
from typing import Optional


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
async def handle_document(message: types.Message, bot: Bot, conn: Optional[sqlite3.Connection] = None): # Add optional conn
    """Handles document messages, expecting an Excel file."""
    if message.document.file_name.endswith(('.xls', '.xlsx')):
        try:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, TEMP_FILE_PATH)

            df = pd.read_excel(TEMP_FILE_PATH)

            required_columns = ['title', 'url', 'xpath']
            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                await message.answer(f"Ошибка: В файле отсутствуют колонки: {', '.join(missing_cols)}.")
                os.remove(TEMP_FILE_PATH)
                return

            # Check if DataFrame is empty after reading
            if df.empty:
                await message.answer("Файл Excel пуст. Данные не загружены.")
                return
            
            output_text = "Содержимое файла:\n\n"
            for _, row in df.iterrows():  # Use _ for unused index
                output_text += f"<b>{row['title']}</b>\n"
                output_text += f"URL: {row['url']}\n"
                output_text += f"XPath: {row['xpath']}\n\n"
            await message.answer(output_text, parse_mode="HTML")

            websites_data = df.to_dict('records')
            save_website_data(websites_data, conn)  # Pass the connection
            await message.answer("Данные сохранены в базу данных.")

        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {e}")
        finally:  # Use finally to *always* delete the file
            if os.path.exists(TEMP_FILE_PATH):
                os.remove(TEMP_FILE_PATH)
    else:
        await message.answer("Пожалуйста, отправьте файл в формате Excel (.xls, .xlsx).")