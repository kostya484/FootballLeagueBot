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
            price INTEGER,
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
                INSERT OR IGNORE INTO teams(
                    name,
                    budget
                )
                VALUES(?,?)
                """,
                (team,budget)
            )


        await db.commit()



async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        count = await cursor.fetchone()


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
                                row.get(
                                    "current_club_name",
                                    "Без клуба"
                                ),
                                row["position"],
                                row["sub_position"],
                                prices.get(
                                    player_id,
                                    0
                                ),
                                None
                            )
                        )


                    except:
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


        return row[0] if row else 0



async def search_player(text):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT id,name,club,position,price
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
            SELECT name,club,position,price
            FROM players
            ORDER BY price DESC
            LIMIT 20
            """
        )

        return await cursor.fetchall()



async def set_owner(user_id, team):

    async with aiosqlite.connect(DB_NAME) as db:

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

        cursor = await db.execute(
            """
            SELECT name
            FROM teams
            WHERE owner_id=?
            """,
            (user_id,)
        )


        row = await cursor.fetchone()


        if row:
            return row[0]

        return None



async def buy_player(player_id, team):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT name,price,owner_team
            FROM players
            WHERE id=?
            """,
            (player_id,)
        )

        player = await cursor.fetchone()


        if not player:
            return "❌ Игрок не найден"


        name,price,owner = player


        if owner:
            return "❌ Игрок уже куплен"



        cursor = await db.execute(
            """
            SELECT budget
            FROM teams
            WHERE name=?
            """,
            (team,)
        )

        money = await cursor.fetchone()


        if not money:
            return "❌ Команда не найдена"


        if money[0] < price:
            return "❌ Не хватает денег"



        await db.execute(
            """
            UPDATE teams
            SET budget = budget - ?
            WHERE name=?
            """,
            (
                price,
                team
            )
        )


        await db.execute(
            """
            UPDATE players
            SET owner_team=?
            WHERE id=?
            """,
            (
                team,
                player_id
            )
        )


        await db.execute(
            """
            INSERT INTO transfers(
                player_name,
                from_team,
                to_team,
                price
            )
            VALUES(?,?,?,?)
            """,
            (
                name,
                "Рынок",
                team,
                price
            )
        )


        await db.commit()


        return (
            f"✅ {name} куплен!\n"
            f"🏟 Команда: {team}\n"
            f"💰 Цена: {format_price(price)}"
        )



def format_price(price):

    if price >= 1000000:
        return f"{price/1000000:.1f} млн €"

    if price >= 1000:
        return f"{price/1000:.0f} тыс €"

    return f"{price} €"
