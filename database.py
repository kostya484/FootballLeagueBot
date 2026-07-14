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
            position TEXT,
            sub_position TEXT,
            price INTEGER DEFAULT 0,
            owner_team TEXT
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            from_team TEXT,
            to_team TEXT,
            price INTEGER
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

        cursor = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        result = await cursor.fetchone()


        if result[0] > 0:
            return



        players_info = {}


        # Загружаем последние клубы и цены
        if os.path.exists("player_valuations.csv"):

            with open(
                "player_valuations.csv",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)


                for row in reader:

                    try:

                        player_id = int(
                            row["player_id"]
                        )

                        date = row["date"]


                        old = players_info.get(
                            player_id
                        )


                        if (
                            old is None
                            or date > old["date"]
                        ):

                            players_info[player_id] = {
                                "date": date,
                                "club": row[
                                    "current_club_name"
                                ],
                                "price": int(
                                    row[
                                        "market_value_in_eur"
                                    ]
                                )
                            }


                    except:
                        pass



        # Загружаем игроков

        if os.path.exists("players.csv"):

            with open(
                "players.csv",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)


                for row in reader:

                    try:

                        player_id = int(
                            row["player_id"]
                        )


                        info = players_info.get(
                            player_id,
                            {}
                        )


                        await db.execute(
                            """
                            INSERT OR IGNORE INTO players(
                                id,
                                name,
                                first_name,
                                last_name,
                                club,
                                position,
                                sub_position,
                                price,
                                owner_team
                            )
                            VALUES(?,?,?,?,?,?,?,?,?)
                            """,
                            (
                                player_id,
                                row["name"],
                                row["first_name"],
                                row["last_name"],
                                info.get(
                                    "club",
                                    "Без клуба"
                                ),
                                row["position"],
                                row["sub_position"],
                                info.get(
                                    "price",
                                    0
                                ),
                                None
                            )
                        )


                    except Exception:
                        pass



        await db.commit()

        print("Игроки загружены")



async def get_teams():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT name,budget
            FROM teams
            """
        )

        return await cursor.fetchall()



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
            LIMIT 10
            """,
            (f"%{text}%",)
        )

        return await cursor.fetchall()



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



def format_price(price):

    if price >= 1000000:
        return f"{price / 1000000:.1f} млн €"


    if price >= 1000:
        return f"{price / 1000:.0f} тыс €"


    return f"{price} €"
