import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from database import (
    create_database,
    import_players,
    get_budget,
    search_player,
    top_players,
    format_price,
    set_owner,
    get_user_team,
    remove_owner,
    buy_player,
    get_squad
)


TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(TOKEN)

dp = Dispatcher()



# =========================
# КЛУБЫ
# =========================

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
                text="🏆 Стать тренером"
            )
        ],
        [
            KeyboardButton(
                text="🚪 Покинуть клуб"
            )
        ],
        [
            KeyboardButton(
                text="💸 Трансферный рынок"
            )
        ],
        [
            KeyboardButton(
                text="👥 Мой состав"
            )
        ],
        [
            KeyboardButton(
                text="⭐ Топ игроков"
            )
        ],
        [
            KeyboardButton(
                text="💰 Мой бюджет"
            )
        ]
    ],
    resize_keyboard=True
)



# =========================
# START
# =========================

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
            "👋 Добро пожаловать!\n\n"
            "Ты свободный менеджер.\n"
            "Можешь искать игроков или стать тренером.",
            reply_markup=main_keyboard
        )



# =========================
# СТАТЬ ТРЕНЕРОМ
# =========================

@dp.message(
    F.text=="🏆 Стать тренером"
)
async def become_manager(message: Message):

    await message.answer(
        "🏟 Выбери клуб:",
        reply_markup=club_keyboard
    )



# =========================
# ВЫБОР КЛУБА
# =========================

@dp.message(F.text.in_(teams))
async def choose_team(message: Message):

    team = message.text.replace(
        "🏟 ",
        ""
    )


    await set_owner(
        message.from_user.id,
        team
    )


    await message.answer(
        f"✅ Теперь ты тренер {team}",
        reply_markup=main_keyboard
    )



# =========================
# ПОКИНУТЬ КЛУБ
# =========================

@dp.message(
    F.text=="🚪 Покинуть клуб"
)
async def leave(message: Message):

    await remove_owner(
        message.from_user.id
    )


    await message.answer(
        "🚪 Ты больше не тренер.\n"
        "Теперь ты свободный менеджер.",
        reply_markup=main_keyboard
    )



# =========================
# БЮДЖЕТ
# =========================

@dp.message(
    F.text=="💰 Мой бюджет"
)
async def budget(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Ты пока без клуба"
        )
        return


    money = await get_budget(team)


    await message.answer(
        f"🏟 {team}\n"
        f"💰 {format_price(money)}"
    )



# =========================
# СОСТАВ
# =========================

@dp.message(
    F.text=="👥 Мой состав"
)
async def squad(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Ты пока без клуба"
        )
        return



    players = await get_squad(team)


    if not players:

        await message.answer(
            "👥 Состав пуст"
        )
        return


    text = f"👥 Состав {team}\n\n"


    for p in players:

        name,pos,price=p

        text += (
            f"⚽ {name}\n"
            f"📍 {pos}\n"
            f"💰 {format_price(price)}\n\n"
        )


    await message.answer(text)



# =========================
# РЫНОК
# =========================

@dp.message(
    F.text=="💸 Трансферный рынок"
)
async def market(message: Message):

    await message.answer(
        "Напиши имя игрока:"
    )



# =========================
# ТОП
# =========================

@dp.message(
    F.text=="⭐ Топ игроков"
)
async def top(message: Message):

    players = await top_players()


    text="⭐ ТОП игроков\n\n"


    for i,p in enumerate(players,1):

        name,club,pos,price=p

        text+=(
            f"{i}. {name}\n"
            f"💰 {format_price(price)}\n\n"
        )


    await message.answer(text)



# =========================
# ПОИСК
# =========================

@dp.message()
async def search(message: Message):

    if message.text.startswith("/"):
        return


    players = await search_player(
        message.text
    )


    if not players:

        await message.answer(
            "❌ Не найден"
        )

        return



    for p in players:

        pid,name,club,pos,price=p


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboard
