import os
import pandas as pd
import sqlite3
from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from db.database import save_website_data, get_all_websites  # Assuming you have a get_all_websites function
from typing import Optional
from parser.parser import get_average_prices


router = Router()
TEMP_FILE_PATH = "data/temp_file.xlsx"  # Consider making this configurable

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handles the /start command.  Provides a welcome message and instructions.
    """
    await message.answer(f"Привет, {message.from_user.full_name}! 👋\n\n"
                         "Отправь мне Excel файл с данными о сайтах для парсинга.\n\n"
                         "Формат файла:\n"
                         "- Колонка 'title' - название сайта\n"
                         "- Колонка 'url' - ссылка на сайт\n"
                         "- Колонка 'xpath' - XPath к элементу с ценой")

@router.message(F.document)
async def handle_document(message: types.Message, bot: Bot, conn: Optional[sqlite3.Connection] = None):
    """
    Handles document messages, expecting an Excel file (.xls, .xlsx).

    Downloads the file, validates its format, saves website data to the database,
    parses the websites, and sends the average prices back to the user.

    Args:
        message: The incoming message object.
        bot: The Bot instance.
        conn: An optional SQLite connection.  If None, a temporary connection will be created
            (and closed) within this function.  This allows the function to be used
            either with an existing connection (for a transaction) or standalone.
    """
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
                os.remove(TEMP_FILE_PATH)  # Clean up even on error
                return

            # Check if DataFrame is empty after reading
            if df.empty:
                await message.answer("Файл Excel пуст. Данные не загружены.")
                return

            # Display the content of the file (for verification)
            output_text = "Содержимое файла:\n\n"
            for _, row in df.iterrows():  # Use _ for unused index variable
                output_text += f"<b>{row['title']}</b>\n"  # Use HTML for bold title
                output_text += f"URL: {row['url']}\n"
                output_text += f"XPath: {row['xpath']}\n\n"
            await message.answer(output_text, parse_mode="HTML")

            websites_data = df.to_dict('records')  # Convert DataFrame to list of dictionaries
            save_website_data(websites_data, conn)  # Save to database (using provided or temporary connection)
            await message.answer("Данные сохранены в базу данных.")

            # --- PARSING ---
            await message.answer("Начинаю парсинг сайтов...")
            try:
                website_averages = get_average_prices(websites_data)  # Get average prices

                output_prices = "Средние цены по сайтам:\n\n"
                for title, average_price in website_averages.items():
                    if average_price is not None:
                        output_prices += f"<b>{title}</b>: {average_price:.2f}\n"  # Format price to 2 decimal places
                    else:
                        output_prices += f"<b>{title}</b>: Цена не найдена\n"  # Indicate if price was not found
                await message.answer(output_prices, parse_mode="HTML")  # Use HTML for bold title

            except Exception as e:
                await message.answer(f"Произошла ошибка при парсинге: {e}")

        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {e}")
        finally:
            # Always remove the temporary file, even if an error occurred
            if os.path.exists(TEMP_FILE_PATH):
                os.remove(TEMP_FILE_PATH)
    else:
        await message.answer("Пожалуйста, отправьте файл в формате Excel (.xls, .xlsx).")

@router.message(F.command.in_(["/help"]))
async def command_help_handler(message: Message) -> None:
    """
    Handles the /help command.  Provides detailed instructions on using the bot.
    """
    await message.answer("Этот бот позволяет загружать Excel файлы для добавления сайтов в базу данных, а также парсит цены с этих сайтов и вычисляет среднюю цену.\n\n"
                         "Инструкция:\n"
                         "1. Отправьте файл напрямую.\n"
                         "2. Прикрепите Excel файл с колонками 'title', 'url', 'xpath'.\n"
                         "3. Бот обработает файл, сохранит данные в базу, выполнит парсинг и выведет средние цены.")