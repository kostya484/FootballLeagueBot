import csv
import os
import aiosqlite

from config import START_BUDGETS


DB_NAME = "league.db"


# =====================
# СОЗДАНИЕ БАЗЫ
# =====================

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
        CREATE TABLE IF NOT EXISTS clubs(
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT,
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
                (
                    team,
                    budget
                )
            )


        await db.commit()



# =====================
# ИМПОРТ КЛУБОВ И ИГРОКОВ
# =====================

async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        count = await cur.fetchone()


        if count[0] > 0:
            return



        # --------
        # клубы
        # --------

        clubs = {}


        with open(
            "clubs.csv",
            encoding="utf-8"
        ) as file:


            reader = csv.DictReader(file)


            for row in reader:

                clubs[
                    row["club_id"]
                ] = row["name"]



                await db.execute(
                    """
                    INSERT OR IGNORE INTO clubs
                    VALUES(?,?)
                    """,
                    (
                        int(row["club_id"]),
                        row["name"]
                    )
                )



        # --------
        # игроки
        # --------


        with open(
            "players.csv",
            encoding="utf-8"
        ) as file:


            reader = csv.DictReader(file)


            for row in reader:


                try:

                    club_id = row[
                        "current_club_id"
                    ]


                    club_name = clubs.get(
                        club_id,
                        "Свободный агент"
                    )


                    await db.execute(
                        """
                        INSERT OR IGNORE INTO players
                        VALUES(?,?,?,?,?,?)
                        """,
                        (
                            int(row["player_id"]),
                            row["name"],
                            club_name,
                            row["position"],
                            1000000,
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
            (
                user_id,
            )
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
            (
                user_id,
            )
        )

        row = await cur.fetchone()

        return row[0] if row else None



# =====================
# СОСТАВ
# =====================

async def create_starting_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
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


        return cur.rowcount



async def get_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            """
            SELECT name,position
            FROM players
            WHERE owner_team=?
            """,
            (
                team,
            )
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
            (
                team,
            )
        )


        row = await cur.fetchone()

        return row[0] if row else 0



def format_price(price):

    return f"{price/1000000:.1f} млн €"
