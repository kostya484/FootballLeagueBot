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
    buy_player
)


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()



# ---------- КЛУБЫ ----------

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
                text="💸 Трансферный рынок"
            )
        ],
        [
            KeyboardButton(
                text="💰 Мой бюджет"
            )
        ],
        [
            KeyboardButton(
                text="🔄 Сменить клуб"
            )
        ],
        [
            KeyboardButton(
                text="⭐ Топ игроков"
            )
        ]
    ],
    resize_keyboard=True
)



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



# ---------- START ----------

@dp.message(CommandStart())
async def start(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if team:

        await message.answer(
            f"⚽ Ты управляешь: {team}",
            reply_markup=main_keyboard
        )

    else:

        await message.answer(
            "⚽ Выбери свой клуб:",
            reply_markup=club_keyboard
        )



# ---------- ВЫБОР КЛУБА ----------

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


    budget = await get_budget(
        team
    )


    await message.answer(
        f"✅ Ты теперь управляешь {team}\n\n"
        f"💰 Бюджет: {format_price(budget)}",
        reply_markup=main_keyboard
    )



# ---------- СМЕНА КЛУБА ----------

@dp.message(
    F.text == "🔄 Сменить клуб"
)
async def change_team(message: Message):

    await message.answer(
        "🔄 Выбери новый клуб:",
        reply_markup=club_keyboard
    )



# ---------- БЮДЖЕТ ----------

@dp.message(
    F.text == "💰 Мой бюджет"
)
async def my_budget(message: Message):

    team = await get_user_team(
        message.from_user.id
    )


    if not team:

        await message.answer(
            "Сначала выбери клуб"
        )
        return


    money = await get_budget(
        team
    )


    await message.answer(
        f"🏟 {team}\n"
        f"💰 {format_price(money)}"
    )



# ---------- РЫНОК ----------

@dp.message(
    F.text == "💸 Трансферный рынок"
)
async def market(message: Message):

    await message.answer(
        "💸 Напиши имя игрока:\n\n"
        "Например:\n"
        "Messi\n"
        "Haaland\n"
        "Mbappe"
    )



# ---------- ТОП ----------

@dp.message(
    F.text == "⭐ Топ игроков"
)
async def top(message: Message):

    players = await top_players()

    text = "⭐ Лучшие игроки:\n\n"


    for i,p in enumerate(players,1):

        name,club,pos,price = p

        text += (
            f"{i}. {name}\n"
            f"🏟 {club}\n"
            f"💰 {format_price(price)}\n\n"
        )


    await message.answer(text)



# ---------- ПОИСК ----------

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



    for p in players:

        player_id,name,club,pos,price = p


        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💰 Купить",
                        callback_data=f"buy_{player_id}"
                    )
                ]
            ]
        )


        await message.answer(
            f"⚽ {name}\n"
            f"🏟 {club}\n"
            f"📍 {pos}\n"
            f"💰 {format_price(price)}",
            reply_markup=buttons
        )



# ---------- ПОКУПКА ----------

@dp.callback_query(
    F.data.startswith("buy_")
)
async def buy(callback: CallbackQuery):

    player_id = int(
        callback.data.split("_")[1]
    )


    team = await get_user_team(
        callback.from_user.id
    )


    if not team:

        await callback.message.answer(
            "Сначала выбери клуб"
        )

        return



    result = await buy_player(
        player_id,
        team
    )


    await callback.message.answer(
        result
    )


    await callback.answer()



# ---------- ЗАПУСК ----------

async def main():

    await create_database()

    await import_players()

    print("Бот запущен")

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
