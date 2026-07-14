import csv
import aiosqlite

from config import START_BUDGETS

DB_NAME = "league.db"


async def create_database():
    async with aiosqlite.connect(DB_NAME) as db:

        # ---------- Команды ----------
        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            owner_id INTEGER,
            budget INTEGER
        )
        """)

        # ---------- Игроки ----------
        await db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            name TEXT,
            club TEXT,
            club_id INTEGER,
            position TEXT,
            sub_position TEXT,
            price INTEGER,
            owner_team TEXT,
            date_of_birth TEXT,
            foot TEXT,
            height INTEGER
        )
        """)

        # ---------- История трансферов ----------
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

        # ---------- Стартовые бюджеты ----------
        for team, budget in START_BUDGETS.items():
            await db.execute(
                """
                INSERT OR IGNORE INTO teams(name,budget)
                VALUES(?,?)
                """,
                (team, budget)
            )

        await db.commit()async def import_players():

    async with aiosqlite.connect(DB_NAME) as db:

        clubs = {}

        with open("clubs.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    clubs[int(row["club_id"])] = row["name"]
                except:
                    pass

        prices = {}

        with open("player_valuations.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                try:
                    player_id = int(row["player_id"])
                    value = int(row["market_value_in_eur"])

                    if player_id not in prices:
                        prices[player_id] = value

                except:
                    pass

        with open("players.csv", "r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                try:

                    player_id = int(row["player_id"])

                    club_id = 0

                    if row["current_club_id"]:
                        club_id = int(row["current_club_id"])

                    club_name = clubs.get(club_id, "Свободный агент")

                    await db.execute("""
                    INSERT OR IGNORE INTO players(
                        id,
                        first_name,
                        last_name,
                        name,
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
                        row["first_name"],
                        row["last_name"],
                        row["name"],
                        club_name,
                        club_id,
                        row["position"],
                        row["sub_position"],
                        prices.get(player_id, 0),
                        None,
                        row["date_of_birth"],
                        row["foot"],
                        int(row["height_in_cm"]) if row["height_in_cm"] else 0
                    ))

                except:
                    pass

        await db.commit()# ---------- Получить бюджеты ----------
async def get_teams():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT name, budget FROM teams ORDER BY name"
        )
        return await cursor.fetchall()


# ---------- Бюджет команды ----------
async def get_budget(team):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT budget FROM teams WHERE name=?",
            (team,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


# ---------- Поиск игрока ----------
async def search_player(name):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                name,
                club,
                position,
                price,
                owner_team
            FROM players
            WHERE name LIKE ?
            LIMIT 20
        """, (f"%{name}%",))

        return await cursor.fetchall()


# ---------- Топ дорогих игроков ----------
async def top_players():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                name,
                club,
                position,
                price
            FROM players
            ORDER BY price DESC
            LIMIT 20
        """)

        return await cursor.fetchall()


# ---------- Купить игрока ----------
async def buy_player(player_id, team_name):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT price
            FROM players
            WHERE id=?
        """, (player_id,))

        player = await cursor.fetchone()

        if player is None:
            return False

        price = player[0]

        cursor = await db.execute("""
            SELECT budget
            FROM teams
            WHERE name=?
        """, (team_name,))

        team = await cursor.fetchone()

        if team is None:
            return False

        budget = team[0]

        if budget < price:
            return False

        await db.execute("""
            UPDATE teams
            SET budget=budget-?
            WHERE name=?
        """, (price, team_name))

        await db.execute("""
            UPDATE players
            SET owner_team=?
            WHERE id=?
        """, (team_name, player_id))

        await db.commit()

        return True


# ---------- Игроки команды ----------
async def get_team_players(team_name):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT
                name,
                position,
                price
            FROM players
            WHERE owner_team=?
            ORDER BY price DESC
        """, (team_name,))

        return await cursor.fetchall()
