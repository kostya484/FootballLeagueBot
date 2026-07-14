import csv
import aiosqlite
import os


DB_NAME = "league.db"


TEAMS = {
    "Интер": 120000000,
    "Милан": 100000000,
    "Ювентус": 150000000,
    "Наполи": 90000000,
    "Рома": 90000000,
    "Лацио": 80000000,
    "Аталанта": 85000000,
    "Болонья": 60000000,
    "Торино": 50000000,
    "Фиорентина": 70000000
}



async def create_database():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams(
            name TEXT PRIMARY KEY,
            budget INTEGER,
            owner_id INTEGER
        )
        """)


        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT,
            club TEXT,
            position TEXT,
            owner_team TEXT
        )
        """)



        for team,budget in TEAMS.items():

            await db.execute(
                """
                INSERT OR IGNORE INTO teams
                VALUES(?,?,NULL)
                """,
                (
                    team,
                    budget
                )
            )


        await db.commit()

        print("База создана")




async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            "SELECT COUNT(*) FROM players"
        )

        count = await cur.fetchone()


        if count[0] > 0:

            print("Игроки уже есть")
            return



        clubs = {}


        if os.path.exists("clubs.csv"):

            with open(
                "clubs.csv",
                encoding="utf-8"
            ) as f:

                reader = csv.DictReader(f)


                for row in reader:

                    clubs[row["club_id"]] = row["name"]



        if not os.path.exists("players.csv"):

            print("НЕТ players.csv")
            return



        with open(
            "players.csv",
            encoding="utf-8"
        ) as f:


            reader = csv.DictReader(f)


            added = 0


            for row in reader:


                try:

                    club = clubs.get(
                        row["current_club_id"],
                        "Нет клуба"
                    )


                    await db.execute(
                        """
                        INSERT OR IGNORE INTO players
                        VALUES(?,?,?,?,NULL)
                        """,
                        (
                            int(row["player_id"]),
                            row["name"],
                            club,
                            row.get("position","")
                        )
                    )


                    added += 1


                except Exception as e:

                    print(e)



        await db.commit()


        print(
            "Добавлено игроков:",
            added
        )





async def set_owner(user_id,team):

    async with aiosqlite.connect(DB_NAME) as db:


        await db.execute(
            """
            UPDATE teams
            SET owner_id=NULL
            """
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





async def create_starting_squad(team):

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            """
            UPDATE players
            SET owner_team=?
            WHERE club LIKE ?
            """,
            (
                team,
                "%"+team+"%"
            )
        )


        await db.commit()


        print(
            "Состав игроков:",
            cur.rowcount
        )


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





async def search_player(text):

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            """
            SELECT id,name,club,position
            FROM players
            WHERE name LIKE ?
            LIMIT 10
            """,
            (
                "%"+text+"%",
            )
        )


        return await cur.fetchall()





async def top_players():

    async with aiosqlite.connect(DB_NAME) as db:


        cur = await db.execute(
            """
            SELECT name,club,position
            FROM players
            LIMIT 20
            """
        )


        return await cur.fetchall()




def format_price(price):

    return f"{price/1000000:.1f} млн €"
