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
    add_player_to_squad,
    top_players,
    search_player,
    format_price
)


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


clubs = [
    "Милан",
    "Интер",
    "Ювентус",
    "Наполи",
    "Рома",
    "Лацио",
    "Аталанта",
    "Торино",
    "Фиорентина",
    "Болонья"
]


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🏆 Выбрать клуб"
            )
        ],
        [
            KeyboardButton(
                text="❌ Покинуть клуб"
            )
        ],
        [
            KeyboardButton(
                text="👥 Игроки клуба"
            )
        ],
        [
            KeyboardButton(
                text="⚽ Создать состав"
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
            "⚽ Добро пожаловать!\n\n"
            "Ты свободный менеджер.\n"
            "Выбери клуб, чтобы стать тренером.",
            reply_markup=main_keyboard
        )



@dp.message(
    F.text == "🏆 Выбрать клуб"
)
async def choose_club(message: Message):

    await message.answer(
        "Выбери клуб:",
        reply_markup=club_keyboard
    )



@dp.message(
    F.text.startswith("🏟 ")
)
async def select_club(message: Message):

    team = message.text.replace(
        "🏟 ",
        ""
    )


    result = set_owner(
        message.from_user.id,
        team
    )


    if result:

        money = get_budget(team)

        await message.answer(
            f"✅ Ты главный тренер {team}\n\n"
            f"💰 Бюджет: {format_price(money)}\n\n"
            "Теперь можешь создать состав.",
            reply_markup=main_keyboard
        )

    else:

        await message.answer(
            "❌ Этот клуб уже занят"
        )



@dp.message(
    F.text == "❌ Покинуть клуб"
)
async def leave_club(message: Message):

    remove_team(
        message.from_user.id
    )

    await message.answer(
        "❌ Ты покинул клуб",
        reply_markup=main_keyboard
    )



@dp.message(
    F.text == "💰 Бюджет"
)
async def show_budget(message: Message):

    team = get_user_team(
        message.from_user.id
    )

    if not team:

        await message.answer(
            "Сначала выбери клуб"
        )

        return


    money = get_budget(team)


    await message.answer(
        f"💰 Бюджет {team}\n\n"
        f"{format_price(money)}"
    )
@dp.message(
    F.text == "👥 Игроки клуба"
)
async def club_players(message: Message):

    team = get_user_team(
        message.from_user.id
    )

    if not team:

        await message.answer(
            "❌ Сначала выбери клуб"
        )

        return


    players = get_all_club_players(
        team
    )


    if not players:

        await message.answer(
            "Игроки не найдены"
        )

        return


    text = (
        f"👥 Игроки {team}\n\n"
        "Отправь ID игрока, "
        "чтобы добавить его в состав.\n\n"
    )


    for player in players[:40]:

        text += (
            f"🆔 {player[0]}\n"
            f"⚽ {player[1]}\n"
            f"📍 {player[2]}\n"
            f"💰 {format_price(player[4])}\n\n"
        )


    await message.answer(text)



@dp.message(
    F.text == "⚽ Создать состав"
)
async def create_squad(message: Message):

    team = get_user_team(
        message.from_user.id
    )

    if not team:

        await message.answer(
            "❌ Сначала выбери клуб"
        )

        return


    await message.answer(
        "⚽ Создание состава\n\n"
        "Открой '👥 Игроки клуба'\n"
        "и отправь ID игроков.\n\n"
        "Нужно выбрать 11 игроков."
    )



@dp.message(
    F.text == "📋 Мой состав"
)
async def my_squad(message: Message):

    players = get_squad(
        message.from_user.id
    )


    if not players:

        await message.answer(
            "❌ Состав пуст"
        )

        return


    text = "📋 Твой стартовый состав:\n\n"


    for player in players:

        text += (
            f"⚽ {player[1]}\n"
            f"📍 {player[2]}\n\n"
        )


    await message.answer(text)



@dp.message(
    F.text == "⭐ Топ игроков"
)
async def top(message: Message):

    players = top_players()


    text = "⭐ ТОП игроков\n\n"


    for player in players:

        text += (
            f"⚽ {player[1]}\n"
            f"🏟 {player[2]}\n"
            f"💰 {format_price(player[3])}\n\n"
        )


    await message.answer(text)
@dp.message()
async def messages(message: Message):

    if message.text.startswith("/"):
        return


    # Добавление игрока по ID
    if message.text.isdigit():

        player_id = int(
            message.text
        )

        result = add_player_to_squad(
            message.from_user.id,
            player_id
        )


        if result:

            await message.answer(
                "✅ Игрок добавлен в состав"
            )

        else:

            await message.answer(
                "❌ Не удалось добавить игрока\n"
                "Возможно уже 11 игроков или он уже есть."
            )

        return



    # Поиск игрока

    players = search_player(
        message.text
    )


    if not players:

        await message.answer(
            "❌ Игрок не найден"
        )

        return


    text = "🔎 Найденные игроки:\n\n"


    for player in players:

        text += (
            f"🆔 {player[0]}\n"
            f"⚽ {player[1]}\n"
            f"🏟 {player[2]}\n"
            f"💰 {format_price(player[4])}\n\n"
        )


    await message.answer(text)



async def main():

    create_database()

    import_players()

    print(
        "Бот запущен"
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(
        main()
)
