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

        result = await cur.fetchone()


        if result[0] > 0:
            return



        clubs = {}


        # читаем клубы

        if os.path.exists("clubs.csv"):

            with open(
                "clubs.csv",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)


                for row in reader:

                    try:

                        clubs[
                            row["club_id"]
                        ] = row["name"]

                    except:

                        pass



        # читаем игроков

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


                        club_id = row.get(
                            "current_club_id",
                            ""
                        )


                        club = clubs.get(
                            club_id,
                            "Свободный агент"
                        )


                        name = row.get(
                            "name",
                            "Unknown"
                        )


                        position = row.get(
                            "position",
                            ""
                        )



                        await db.execute(
                            """
                            INSERT OR IGNORE INTO players
                            (
                            id,
                            name,
                            club,
                            position,
                            price,
                            owner_team
                            )
                            VALUES(?,?,?,?,?,?)
                            """,
                            (
                                player_id,
                                name,
                                club,
                                position,
                                1000000,
                                None
                            )
                        )


                    except Exception as e:

                        print(
                            "Ошибка игрока:",
                            e
                        )



        await db.commit()

        print("Игроки загружены")



# =========================
# ТРЕНЕР
# =========================


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


        if row:

            return row[0]


        return None



# =========================
# СОСТАВ
# =========================


async def create_starting_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:


        club_search = {

            "Интер":"Inter",
            "Милан":"Milan",
            "Ювентус":"Juventus",
            "Наполи":"Napoli",
            "Рома":"Roma",
            "Лацио":"Lazio",
            "Аталанта":"Atalanta",
            "Болонья":"Bologna",
            "Торино":"Torino",
            "Фиорентина":"Fiorentina"

        }


        search = club_search.get(
            team,
            team
        )


        cur = await db.execute(
            """
            UPDATE players
            SET owner_team=?
            WHERE club LIKE ?
            """,
            (
                team,
                f"%{search}%"
            )
        )


        await db.commit()


        return cur.rowcount



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



# =========================
# БЮДЖЕТ
# =========================


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



# =========================
# ПОИСК
# =========================


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
