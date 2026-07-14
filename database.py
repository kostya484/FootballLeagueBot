import csv
import os
import aiosqlite

from config import START_BUDGETS


DB_NAME = "league.db"



async def create_database():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            owner_id INTEGER,
            budget INTEGER
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT,
            first_name TEXT,
            last_name TEXT,
            club TEXT,
            position TEXT,
            price INTEGER,
            owner_team TEXT
        )
        """)


        for team,budget in START_BUDGETS.items():

            await db.execute(
                """
                INSERT OR IGNORE INTO teams
                (name,budget)
                VALUES(?,?)
                """,
                (team,budget)
            )


        await db.commit()



async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        count = await cur.fetchone()

        if count[0] > 0:
            return



        prices = {}


        if os.path.exists("player_valuations.csv"):

            with open(
                "player_valuations.csv",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:

                    try:

                        prices[int(row["player_id"])] = int(
                            row["market_value_in_eur"]
                        )

                    except:
                        pass



        with open(
            "players.csv",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                try:

                    pid = int(row["player_id"])


                    await db.execute(
                        """
                        INSERT INTO players
                        VALUES(?,?,?,?,?,?,?,?)
                        """,
                        (
                            pid,
                            row["name"],
                            row["first_name"],
                            row["last_name"],
                            row["current_club"],
                            row["position"],
                            prices.get(pid,0),
                            None
                        )
                    )


                except:
                    pass



        await db.commit()



# =====================
# ТРЕНЕР
# =====================


async def set_owner(user_id,team):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE teams
            SET owner_id=NULL
            WHERE owner_id=?
            """,
            (user_id,)
        )


        await db.execute(
            """
            UPDATE teams
            SET owner_id=?
            WHERE name=?
            """,
            (
                user_id,
                team
            )
        )


        await db.commit()



async def get_user_team(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT name
            FROM teams
            WHERE owner_id=?
            """,
            (user_id,)
        )

        row = await cur.fetchone()

        return row[0] if row else None



# =====================
# СТАРТОВЫЙ СОСТАВ
# =====================


async def create_starting_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE players
            SET owner_team=?
            WHERE club=?
            """,
            (
                team,
                team
            )
        )


        await db.commit()



async def get_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT name,position,price
            FROM players
            WHERE owner_team=?
            """,
            (team,)
        )

        return await cur.fetchall()



# =====================
# БЮДЖЕТ
# =====================


async def get_budget(team):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT budget
            FROM teams
            WHERE name=?
            """,
            (team,)
        )

        row = await cur.fetchone()

        return row[0] if row else 0



# =====================
# ПОИСК
# =====================


async def search_player(text):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT id,name,club,position,price
            FROM players
            WHERE name LIKE ?
            LIMIT 10
            """,
            (
                f"%{text}%",
            )
        )

        return await cur.fetchall()



async def top_players():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT name,club,position,price
            FROM players
            ORDER BY price DESC
            LIMIT 20
            """
        )

        return await cur.fetchall()



def format_price(price):

    if price >= 1000000:
        return f"{price/1000000:.1f} млн €"

    return f"{price} €"
