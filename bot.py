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
    remove_team,
    get_user_team,
    get_budget,
    get_all_club_players,
    get_squad,
    buy_player,
    top_players,
    search_player,
    get_transfers,
    get_all_squads,
    format_price
)



TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 123456789  # <-- сюда свой Telegram ID



bot = Bot(TOKEN)

dp = Dispatcher()



main_keyboard = ReplyKeyboardMarkup(

    keyboard=[

        [
            KeyboardButton(
                text="🏆 Выбрать клуб"
            )
        ],

        [
            KeyboardButton(
                text="👥 Игроки клуба"
            )
        ],

        [
            KeyboardButton(
                text="💸 Трансферный рынок"
            )
        ],

        [
            KeyboardButton(
                text="📋 Мой состав"
            )
        ],

        [
            KeyboardButton(
                text="💰 Бюджет"
            )
        ],

        [
            KeyboardButton(
                text="⭐ Топ игроков"
            )
        ],

        [
            KeyboardButton(
                text="❌ Покинуть клуб"
            )
        ],

        [
            KeyboardButton(
                text="👑 Админ"
            )
        ]

    ],

    resize_keyboard=True
)



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
            KeyboardButton(text="🏟 Аталанта"),
            KeyboardButton(text="🏟 Торино")
        ],

        [
            KeyboardButton(text="🏟 Фиорентина"),
            KeyboardButton(text="🏟 Болонья")
        ]

    ],

    resize_keyboard=True
)





@dp.message(CommandStart())
async def start(message: Message):

    team = get_user_team(
        message.from_user.id
    )


    if team:

        await message.answer(
            f"👔 Ты тренер {team}",
            reply_markup=main_keyboard
        )


    else:

        await message.answer(
            "⚽ Добро пожаловать!\n"
            "Выбери клуб.",
            reply_markup=main_keyboard
        )





@dp.message(F.text=="🏆 Выбрать клуб")
async def clubs(message:Message):

    await message.answer(
        "Выбери клуб:",
        reply_markup=club_keyboard
    )





@dp.message(F.text.startswith("🏟 "))
async def choose_club(message:Message):

    team = message.text.replace(
        "🏟 ",
        ""
    )


    result=set_owner(
        message.from_user.id,
        team
    )


    if result:

        await message.answer(
            f"✅ Ты тренер {team}\n"
            f"💰 {format_price(get_budget(team))}",
            reply_markup=main_keyboard
        )


    else:

        await message.answer(
            "❌ Клуб уже занят"
        )





@dp.message(F.text=="💰 Бюджет")
async def budget(message:Message):

    team=get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Нет клуба"
        )
        return


    await message.answer(
        format_price(
            get_budget(team)
        )
    )





@dp.message(F.text=="👥 Игроки клуба")
async def players(message:Message):

    team=get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Сначала выбери клуб"
        )
        return



    data=get_all_club_players(
        team
    )


    text="👥 Игроки:\n\n"


    for p in data:

        text+=(
            f"🆔 {p[0]}\n"
            f"⚽ {p[1]}\n"
            f"📍 {p[2]}\n"
            f"💰 {format_price(p[4])}\n\n"
        )


    await message.answer(text)





@dp.message(F.text=="💸 Трансферный рынок")
async def market(message:Message):

    await message.answer(
        "💸 Напиши ID игрока для покупки"
    )





@dp.message(F.text=="📋 Мой состав")
async def squad(message:Message):

    data=get_squad(
        message.from_user.id
    )


    text="📋 Состав:\n\n"


    for p in data:

        text+=(
            f"⚽ {p[1]}\n"
            f"📍 {p[2]}\n\n"
        )


    await message.answer(text)





@dp.message(F.text=="⭐ Топ игроков")
async def top(message:Message):

    data=top_players()


    text="⭐ ТОП:\n\n"


    for p in data:

        text+=(
            f"⚽ {p[1]}\n"
            f"🏟 {p[2]}\n"
            f"💰 {format_price(p[3])}\n\n"
        )


    await message.answer(text)
