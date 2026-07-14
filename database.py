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
    get_teams,
    get_budget,
    search_player,
    top_players
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
            KeyboardButton(text="🏟 Сассуоло"),
            KeyboardButton(text="🏟 Фиорентина")
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
        "👋 Добро пожаловать в виртуальную футбольную лигу!\n\n"
        "Выберите действие:",
        reply_markup=keyboard
)
  import csv
import os
import aiosqlite

from config import START_BUDGETS

DB_NAME = "league.db"


async def create_database():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            owner_id INTEGER,
            budget INTEGER
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            first_name TEXT,
            last_name TEXT,
            club TEXT,
            club_id INTEGER,
            position TEXT,
            sub_position TEXT,
            price INTEGER DEFAULT 0,
            owner_team TEXT,
            date_of_birth TEXT,
            foot TEXT,
            height INTEGER
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            player_name TEXT,
            from_team TEXT,
            to_team TEXT,
            price INTEGER,
            transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


        for team, budget in START_BUDGETS.items():

            await db.execute(
                """
                INSERT OR IGNORE INTO teams(name,budget)
                VALUES(?,?)
                """,
                (team, budget)
            )


        await db.commit()

  async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:

        # Проверяем, импортировали ли уже игроков
        cursor = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        count = await cursor.fetchone()

        if count[0] > 0:
            return


        # ---------- КЛУБЫ ----------
        clubs = {}

        if os.path.exists("clubs.csv"):

            with open(
                "clubs.csv",
                "r",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:

                    try:
                        clubs[int(row["club_id"])] = row["name"]

                    except:
                        pass



        # ---------- ЦЕНЫ ----------
        prices = {}

        if os.path.exists("player_valuations.csv"):

            with open(
                "player_valuations.csv",
                "r",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:

                    try:

                        player_id = int(row["player_id"])

                        prices[player_id] = int(
                            row["market_value_in_eur"]
                        )

                    except:
                        pass



        # ---------- ИГРОКИ ----------
        if os.path.exists("players.csv"):

            with open(
                "players.csv",
                "r",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)


                for row in reader:

                    try:

                        player_id = int(row["player_id"])

                        club_id = 0

                        if row["current_club_id"]:
                            club_id = int(
                                row["current_club_id"]
                            )


                        club = clubs.get(
                            club_id,
                            "Свободный агент"
                        )


                        await db.execute(
                            """
                            INSERT OR IGNORE INTO players(
                                id,
                                name,
                                first_name,
                                last_name,
                                club,
                                club_id,
                                position,
                                sub_position,
                                price,
                                owner_team,
                                date_of_birth,
                                foot,
                                height
                            )
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """,
                            (
                                player_id,
                                row["name"],
                                row["first_name"],
                                row["last_name"],
                                club,
                                club_id,
                                row["position"],
                                row["sub_position"],
                                prices.get(
                                    player_id,
                                    0
                                ),
                                None,
                                row["date_of_birth"],
                                row["foot"],
                                row["height_in_cm"]
                            )
                        )


                    except Exception:
                        pass


        await db.commit()

    # ---------- Получить команды ----------

async def get_teams():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT name, budget
            FROM teams
            ORDER BY name
            """
        )

        return await cursor.fetchall()



# ---------- Получить бюджет ----------

async def get_budget(team):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT budget
            FROM teams
            WHERE name=?
            """,
            (team,)
        )

        row = await cursor.fetchone()

        if row:
            return row[0]

        return 0



# ---------- Поиск игроков ----------

async def search_player(text):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                id,
                name,
                club,
                position,
                price
            FROM players
            WHERE name LIKE ?
            ORDER BY price DESC
            LIMIT 10
            """,
            (f"%{text}%",)
        )

        return await cursor.fetchall()



# ---------- Топ игроков ----------

async def top_players():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                name,
                club,
                position,
                price
            FROM players
            ORDER BY price DESC
            LIMIT 20
            """
        )

        return await cursor.fetchall()



# ---------- Купить игрока ----------

async def buy_player(player_id, team):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT name, price, owner_team
            FROM players
            WHERE id=?
            """,
            (player_id,)
        )

        player = await cursor.fetchone()


        if not player:
            return False


        name, price, owner = player


        if owner:
            return False



        cursor = await db.execute(
            """
            SELECT budget
            FROM teams
            WHERE name=?
            """,
            (team,)
        )

        budget = await cursor.fetchone()


        if not budget:
            return False



        if budget[0] < price:
            return False



        await db.execute(
            """
            UPDATE teams
            SET budget = budget - ?
            WHERE name=?
            """,
            (price, team)
        )


        await db.execute(
            """
            UPDATE players
            SET owner_team=?
            WHERE id=?
            """,
            (team, player_id)
        )


        await db.execute(
            """
            INSERT INTO transfers(
                player_id,
                player_name,
                from_team,
                to_team,
                price
            )
            VALUES(?,?,?,?,?)
            """,
            (
                player_id,
                name,
                "Свободный рынок",
                team,
                price
            )
        )


        await db.commit()

        return True

  # ---------- Игроки команды ----------

async def get_team_players(team):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                name,
                position,
                club,
                price
            FROM players
            WHERE owner_team=?
            ORDER BY price DESC
            """,
            (team,)
        )

        return await cursor.fetchall()



# ---------- Формат цены ----------

def format_price(price):

    if price >= 1_000_000_000:
        return f"{price / 1_000_000_000:.1f} млрд €"

    if price >= 1_000_000:
        return f"{price / 1_000_000:.1f} млн €"

    if price >= 1_000:
        return f"{price / 1_000:.0f} тыс €"

    return f"{price} €"
