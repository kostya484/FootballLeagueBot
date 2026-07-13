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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            position TEXT,
            club TEXT,
            price INTEGER,
            team TEXT
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
                "INSERT OR IGNORE INTO teams(name,budget) VALUES(?,?)",
                (team, budget)
            )

        await db.commit()


async def get_teams():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT name,budget FROM teams"
        )
        return await cursor.fetchall()


async def get_budget(team):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT budget FROM teams WHERE name=?",
            (team,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None
