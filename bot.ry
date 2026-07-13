import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database import create_database, get_teams, get_budget

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


# ---------- КЛАВИАТУРА ----------
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏟 Милан"), KeyboardButton(text="🏟 Интер")],
        [KeyboardButton(text="🏟 Ювентус"), KeyboardButton(text="🏟 Наполи")],
        [KeyboardButton(text="🏟 Рома"), KeyboardButton(text="🏟 Комо")],
        [KeyboardButton(text="🏟 Болонья"), KeyboardButton(text="🏟 Торино")],
        [KeyboardButton(text="🏟 Сассуоло"), KeyboardButton(text="🏟 Фиорентина")],
        [KeyboardButton(text="💰 Бюджеты команд")]
    ],
    resize_keyboard=True
)


# ---------- /start ----------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в виртуальную футбольную лигу!\n\n"
        "Выберите команду:",
        reply_markup=keyboard
    )


# ---------- БЮДЖЕТЫ ----------
@dp.message(Command("teams"))
@dp.message(F.text == "💰 Бюджеты команд")
async def teams(message: Message):
    teams = await get_teams()

    text = "💰 Бюджеты команд:\n\n"

    for team, budget in teams:
        text += f"⚽ {team} — ${budget:,}\n"

    await message.answer(text)


# ---------- ИНФОРМАЦИЯ О КОМАНДАХ ----------
@dp.message(
    F.text.in_([
        "🏟 Милан",
        "🏟 Интер",
        "🏟 Ювентус",
        "🏟 Наполи",
        "🏟 Рома",
        "🏟 Комо",
        "🏟 Болонья",
        "🏟 Торино",
        "🏟 Сассуоло",
        "🏟 Фиорентина"
    ])
)
async def team_info(message: Message):

    team = message.text.replace("🏟 ", "")

    budget = await get_budget(team)

    await message.answer(
        f"🏟 <b>{team}</b>\n\n"
        f"💰 Бюджет: <b>${budget:,}</b>\n\n"
        f"⚽ Скоро здесь появятся:\n"
        f"• состав команды\n"
        f"• трансферы\n"
        f"• статистика\n"
        f"• результаты матчей",
        parse_mode="HTML"
    )


async def main():
    await create_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
