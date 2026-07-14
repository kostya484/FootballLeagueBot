import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database import (
    create_database,
    import_players,
    get_teams,
    get_budget,
    search_player,
    top_players,
    format_price
)


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏟 Милан"),
            KeyboardButton(text="🏟 Интер")
        ],
        [
            KeyboardButton(text="🏟 Ювентус"),
            KeyboardButton(text="🏟 Наполи")
        ],
        [
            KeyboardButton(text="🏟 Рома"),
            KeyboardButton(text="🏟 Комо")
        ],
        [
            KeyboardButton(text="🏟 Болонья"),
            KeyboardButton(text="🏟 Торино")
        ],
        [
            KeyboardButton(text="💰 Бюджеты команд")
        ],
        [
            KeyboardButton(text="💸 Трансферный рынок")
        ],
        [
            KeyboardButton(text="⭐ Топ игроков")
        ]
    ],
    resize_keyboard=True
)



@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "⚽ Добро пожаловать в футбольную лигу!\n\n"
        "Выбери действие:",
        reply_markup=keyboard
    )



# ---------- БЮДЖЕТЫ ----------

@dp.message(F.text == "💰 Бюджеты команд")
async def budgets(message: Message):

    teams = await get_teams()

    text = "💰 Бюджеты команд:\n\n"

    for team, budget in teams:

        text += (
            f"🏟 {team} — "
            f"{format_price(budget)}\n"
        )

    await message.answer(text)



# ---------- КОМАНДЫ ----------

@dp.message(
    F.text.in_(
        [
            "🏟 Милан",
            "🏟 Интер",
            "🏟 Ювентус",
            "🏟 Наполи",
            "🏟 Рома",
            "🏟 Комо",
            "🏟 Болонья",
            "🏟 Торино"
        ]
    )
)
async def team_info(message: Message):

    team = message.text.replace(
        "🏟 ",
        ""
    )

    budget = await get_budget(team)

    await message.answer(
        f"🏟 {team}\n\n"
        f"💰 Бюджет: {format_price(budget)}\n\n"
        "Скоро:\n"
        "⚽ состав\n"
        "💸 трансферы\n"
        "📊 статистика"
    )



# ---------- РЫНОК ----------

@dp.message(F.text == "💸 Трансферный рынок")
async def market(message: Message):

    await message.answer(
        "💸 Трансферный рынок открыт!\n\n"
        "Напиши имя игрока.\n\n"
        "Примеры:\n"
        "Messi\n"
        "Mbappe\n"
        "Haaland"
    )



# ---------- ТОП ИГРОКОВ ----------

@dp.message(F.text == "⭐ Топ игроков")
async def top(message: Message):

    players = await top_players()

    text = "⭐ Топ игроков:\n\n"

    number = 1

    for player in players:

        name, club, position, price = player

        text += (
            f"{number}. {name}\n"
            f"🏟 {club}\n"
            f"📍 {position}\n"
            f"💰 {format_price(price)}\n\n"
        )

        number += 1


    await message.answer(text)



# ---------- ПОИСК ИГРОКОВ ----------

@dp.message()
async def search(message: Message):

    text = message.text


    if text.startswith("/"):
        return


    players = await search_player(text)


    if not players:

        await message.answer(
            "❌ Игрок не найден.\n"
            "Попробуй написать на английском."
        )

        return



    answer = "🔍 Найденные игроки:\n\n"


    for player in players:

        player_id, name, club, position, price = player


        answer += (
            f"⚽ {name}\n"
            f"🏟 {club}\n"
            f"📍 {position}\n"
            f"💰 {format_price(price)}\n"
            f"🆔 {player_id}\n\n"
        )


    await message.answer(answer)



# ---------- ЗАПУСК ----------

async def main():

    await create_database()

    await import_players()

    print("Бот запущен")

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
