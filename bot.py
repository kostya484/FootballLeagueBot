import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from database import (
    create_database,
    import_players,
    set_owner,
    get_user_team,
    create_starting_squad,
    get_squad,
    get_budget,
    search_player,
    top_players,
    format_price
)


TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(TOKEN)
dp = Dispatcher()



teams = [
    "🏟 Милан",
    "🏟 Интер",
    "🏟 Ювентус",
    "🏟 Наполи",
    "🏟 Рома",
    "🏟 Лацио",
    "🏟 Фиорентина",
    "🏟 Болонья",
    "🏟 Торино",
    "🏟 Аталанта"
]


club_keyboard = ReplyKeyboardMarkup(
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
            KeyboardButton(text="🏟 Лацио")
        ],
        [
            KeyboardButton(text="🏟 Фиорентина"),
            KeyboardButton(text="🏟 Болонья")
        ],
        [
            KeyboardButton(text="🏟 Торино"),
            KeyboardButton(text="🏟 Аталанта")
        ]
    ],
    resize_keyboard=True
)



main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🏆 Выбрать клуб"
            )
        ],
        [
            KeyboardButton(
                text="⚽ Создать стартовый состав"
            )
        ],
        [
            KeyboardButton(
                text="👥 Мой состав"
            )
        ],
        [
            KeyboardButton(
                text="💸 Трансферный рынок"
            )
        ],
        [
            KeyboardButton(
                text="⭐ Топ игроков"
            )
        ],
        [
            KeyboardButton(
                text="💰 Бюджет"
            )
        ]
    ],
    resize_keyboard=True
)



@dp.message(CommandStart())
async def start(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if team:

        await message.answer(
            f"👔 Ты тренер {team}",
            reply_markup=main_keyboard
        )

    else:

        await message.answer(
            "⚽ Добро пожаловать!\n\n"
            "Ты свободный менеджер.\n"
            "Выбери клуб, чтобы стать тренером.",
            reply_markup=main_keyboard
        )



@dp.message(
    F.text=="🏆 Выбрать клуб"
)
async def choose(message: Message):

    await message.answer(
        "Выбери клуб:",
        reply_markup=club_keyboard
    )



@dp.message(F.text.in_(teams))
async def take_team(message: Message):

    team = message.text.replace(
        "🏟 ",
        ""
    )


    await set_owner(
        message.from_user.id,
        team
    )


    budget = await get_budget(team)


    await message.answer(
        f"✅ Ты главный тренер {team}\n\n"
        f"💰 Бюджет: {format_price(budget)}\n\n"
        "Теперь создай стартовый состав.",
        reply_markup=main_keyboard
    )



@dp.message(
    F.text=="⚽ Создать стартовый состав"
)
async def create_squad(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Сначала выбери клуб"
        )

        return


    await create_starting_squad(team)


    await message.answer(
        f"⚽ Стартовый состав {team} создан!"
    )



@dp.message(
    F.text=="👥 Мой состав"
)
async def squad(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "У тебя нет клуба"
        )

        return



    players = await get_squad(team)


    if not players:

        await message.answer(
            "Сначала создай стартовый состав"
        )

        return



    text = f"👥 {team}\n\n"


    for p in players:

        name,pos,price = p

        text += (
            f"⚽ {name}\n"
            f"📍 {pos}\n"
            f"💰 {format_price(price)}\n\n"
        )


    await message.answer(text)



@dp.message(
    F.text=="💰 Бюджет"
)
async def budget(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Нет клуба"
        )

        return


    money = await get_budget(team)


    await message.answer(
        f"💰 {format_price(money)}"
    )



@dp.message(
    F.text=="💸 Трансферный рынок"
)
async def market(message: Message):

    await message.answer(
        "Напиши имя игрока"
    )



@dp.message(
    F.text=="⭐ Топ игроков"
)
async def top(message: Message):

    players = await top_players()

    text="⭐ ТОП игроков\n\n"


    for p in players:

        text += (
            f"⚽ {p[0]}\n"
            f"💰 {format_price(p[3])}\n\n"
        )


    await message.answer(text)



@dp.message()
async def search(message: Message):

    if message.text.startswith("/"):
        return


    players = await search_player(
        message.text
    )


    if not players:

        await message.answer(
            "❌ Игрок не найден"
        )

        return


    text="🔎 Игроки:\n\n"


    for p in players:

        text += (
            f"⚽ {p[1]}\n"
            f"🏟 {p[2]}\n"
            f"💰 {format_price(p[4])}\n\n"
        )


    await message.answer(text)



async def main():

    await create_database()

    await import_players()

    print("Бот запущен")

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
