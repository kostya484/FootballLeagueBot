import sqlite3
import csv
import os

DB = "league.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()
def set_owner(user_id, team):
def search_player(text):
def buy_player(user_id, player_id):

    team = get_user_team(user_id)

    if not team:
        return False

    cursor.execute("""
    SELECT club,price
    FROM players
    WHERE id=?
    """,(player_id,))

    row = cursor.fetchone()

    if row is None:
        return False

    old_club, price = row

    if old_club == team:
        return False

    budget = get_budget(team)

    if budget < price:
        return False

    cursor.execute("""
    UPDATE clubs
    SET budget=budget-?
    WHERE name=?
    """,(price,team))

    cursor.execute("""
    UPDATE clubs
    SET budget=budget+?
    WHERE name=?
    """,(price,old_club))

    cursor.execute("""
    UPDATE players
    SET club=?
    WHERE id=?
    """,(team,player_id))

    conn.commit()

    return True


def sell_player(user_id, player_id):

    team = get_user_team(user_id)

    if not team:
        return False

    cursor.execute("""
    SELECT club,price
    FROM players
    WHERE id=?
    """,(player_id,))

    row = cursor.fetchone()

    if row is None:
        return False

    if row[0] != team:
        return False

    cursor.execute("""
    UPDATE clubs
    SET budget=budget+?
    WHERE name=?
    """,(row[1],team))

    cursor.execute("""
    UPDATE players
    SET club='Свободный агент'
    WHERE id=?
    """,(player_id,))

    cursor.execute("""
    DELETE FROM squad
    WHERE user_id=? AND player_id=?
    """,(user_id,player_id))

    conn.commit()

    return True


def close_database():
    conn.commit()
    conn.close()

    cursor.execute("""
    SELECT
    id,
    name,
    club,
    position,
    price
    FROM players
    WHERE name LIKE ?
    ORDER BY price DESC
    LIMIT 20
    """, (f"%{text}%",))

    return cursor.fetchall()


def top_players():

    cursor.execute("""
    SELECT
    id,
    name,
    club,
    price
    FROM players
    ORDER BY price DESC
    LIMIT 20
    """)

    return cursor.fetchall()


def get_all_club_players(team):

    cursor.execute("""
    SELECT
    id,
    name,
    position,
    sub_position,
    price
    FROM players
    WHERE club=?
    ORDER BY price DESC
    """, (team,))

    return cursor.fetchall()


def get_squad(user_id):

    cursor.execute("""
    SELECT
    players.id,
    players.name,
    players.position,
    players.sub_position,
    players.price
    FROM squad
    JOIN players
    ON players.id=squad.player_id
    WHERE squad.user_id=?
    """, (user_id,))

    return cursor.fetchall()


def add_player_to_squad(user_id, player_id):

    cursor.execute("""
    SELECT COUNT(*)
    FROM squad
    WHERE user_id=?
    """, (user_id,))

    if cursor.fetchone()[0] >= 11:
        return False

    cursor.execute("""
    SELECT *
    FROM squad
    WHERE user_id=? AND player_id=?
    """, (user_id, player_id))

    if cursor.fetchone():
        return False

    cursor.execute("""
    INSERT INTO squad(user_id,player_id)
    VALUES(?,?)
    """, (user_id, player_id))

    conn.commit()

    return True


def clear_squad(user_id):

    cursor.execute("""
    DELETE FROM squad
    WHERE user_id=?
    """, (user_id,))

    conn.commit()

    cursor.execute(
        "SELECT owner FROM clubs WHERE name=?",
        (team,)
    )

    row = cursor.fetchone()

    if row is None:
        return False

    if row[0] not in (None, user_id):
        return False

    cursor.execute(
        "UPDATE users SET team=NULL WHERE user_id=?",
        (user_id,)
    )

    cursor.execute("""
    INSERT OR IGNORE INTO users(user_id,team)
    VALUES(?,?)
    """,(user_id,team))

    cursor.execute("""
    UPDATE users
    SET team=?
    WHERE user_id=?
    """,(team,user_id))

    cursor.execute("""
    UPDATE clubs
    SET owner=?
    WHERE name=?
    """,(user_id,team))

    conn.commit()

    return True


def remove_team(user_id):

    team = get_user_team(user_id)

    if team is None:
        return

    cursor.execute("""
    UPDATE clubs
    SET owner=NULL
    WHERE name=?
    """,(team,))

    cursor.execute("""
    UPDATE users
    SET team=NULL
    WHERE user_id=?
    """,(user_id,))

    cursor.execute("""
    DELETE FROM squad
    WHERE user_id=?
    """,(user_id,))

    conn.commit()


def get_user_team(user_id):

    cursor.execute(
        "SELECT team FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return None


def get_budget(team):

    cursor.execute(
        "SELECT budget FROM clubs WHERE name=?",
        (team,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return 0


def format_price(price):

    return f"{price:,} €".replace(",", " ")


def create_database():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clubs(
        name TEXT PRIMARY KEY,
        budget INTEGER,
        owner INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY,
        name TEXT,
        club TEXT,
        position TEXT,
        sub_position TEXT,
        price INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        team TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS squad(
        user_id INTEGER,
        player_id INTEGER
    )
    """)

    conn.commit()


def import_players():

    cursor.execute("SELECT COUNT(*) FROM players")

    if cursor.fetchone()[0] > 0:
        print("Игроки уже добавлены")
        return

    budgets = {
        "Милан":120000000,
        "Интер":120000000,
        "Ювентус":120000000,
        "Наполи":120000000,
        "Рома":120000000,
        "Лацио":120000000,
        "Аталанта":120000000,
        "Торино":120000000,
        "Фиорентина":120000000,
        "Болонья":120000000
    }

    for club,budget in budgets.items():

        cursor.execute(
            """
            INSERT OR IGNORE INTO clubs
            VALUES(?,?,NULL)
            """,
            (club,budget)
        )

    mapping = {
        "Inter Milan":"Интер",
        "AC Milan":"Милан",
        "Juventus":"Ювентус",
        "Napoli":"Наполи",
        "Roma":"Рома",
        "AS Roma":"Рома",
        "Lazio":"Лацио",
        "Atalanta":"Аталанта",
        "Torino":"Торино",
        "Fiorentina":"Фиорентина",
        "Bologna":"Болонья"
    }

    with open(
        "players.csv",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            club = mapping.get(
                row["current_club_name"]
            )

            if not club:
                continue

            price = row["market_value_in_eur"]

            if price == "":
                price = 0

            else:
                price = int(price.replace(",",""))

            cursor.execute("""
            INSERT INTO players
            VALUES(?,?,?,?,?,?)
            """,(
                int(row["player_id"]),
                row["name"],
                club,
                row["position"],
                row["sub_position"],
                price
            ))

    conn.commit()

    print("База создана")
