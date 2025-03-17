import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers import basic  # Импортируем handlers
from config import BOT_TOKEN
from db.database import init_db

load_dotenv()

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрация handlers
    dp.include_router(basic.router)

    # Установка команд бота (для отображения в меню)
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Помощь")
    ])

    init_db()

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())