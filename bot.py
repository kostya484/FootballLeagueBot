import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database import create_database, get_teams

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в виртуальную футбольную лигу!\n\n"
        "Доступные команды:\n"
        "🏟 Милан\n"
        "🏟 Интер\n"
        "🏟 Ювентус\n"
        "🏟 Наполи\n"
        "🏟 Рома\n"
        "🏟 Комо\n"
        "🏟 Болонья\n"
        "🏟 Торино\n"
        "🏟 Сассуоло\n"
        "🏟 Фиорентина"
    )


@dp.message(Command("teams"))
async def teams(message: Message):
    teams = await get_teams()

    text = "💰 Бюджеты команд:\n\n"

    for team, budget in teams:
        text += f"⚽ {team} — ${budget:,}\n"

    await message.answer(text)


async def main():
    await create_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
