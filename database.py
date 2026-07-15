import sqlite3
import pandas as pd
from datetime import datetime

DB = "football.db"


def connect():
    return sqlite3.connect(DB)


# ==========================
# СОЗДАНИЕ БАЗЫ
# ==========================

def create_database():

    con = connect()
    cur = con.cursor()

    # Пользователи
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        club TEXT
    )
    """)

    # Клубы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clubs(
        name TEXT PRIMARY KEY,
        tm_name TEXT,
        budget INTEGER,
        owner INTEGER
    )
    """)

    # Игроки
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INTEGER PRIMARY KEY,
        name TEXT,
        club TEXT,
        position TEXT,
        price INTEGER
    )
    """)

    # Состав
    cur.execute("""
    CREATE TABLE IF NOT EXISTS squads(
        user_id INTEGER,
        player_id INTEGER
    )
    """)

    # История трансферов
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transfers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        player_id INTEGER,
        player_name TEXT,
        price INTEGER,
        action TEXT,
        date TEXT
    )
    """)

    # Тактики
    cur.execute("""
    CREATE TABLE IF NOT EXISTS formations(
        user_id INTEGER PRIMARY KEY,
        formation TEXT
    )
    """)

    clubs = [
        ("Интер", "Inter Milan", 450000000),
        ("Милан", "AC Milan", 420000000),
        ("Ювентус", "Juventus", 520000000),
        ("Наполи", "Napoli", 390000000),
        ("Рома", "AS Roma", 310000000),
        ("Лацио", "Lazio", 260000000),
        ("Аталанта", "Atalanta", 240000000),
        ("Торино", "Torino", 180000000),
        ("Фиорентина", "Fiorentina", 220000000),
        ("Болонья", "Bologna", 170000000)
    ]

    for club in clubs:
        cur.execute("""
        INSERT OR IGNORE INTO clubs
        VALUES(?,?,?,?)
        """, club)

    con.commit()
    con.close()


# ==========================
# ЗАГРУЗКА ИГРОКОВ
# ==========================

def import_players():

    con = connect()

    try:
        df = pd.read_csv("players.csv")
    except Exception as e:
        print("Ошибка players.csv:", e)
        return

    cur = con.cursor()

    cur.execute("DELETE FROM players")

    for _, p in df.iterrows():

        try:
            price = int(str(p["market_value_in_eur"]).replace(",", ""))
        except:
            price = 0

        cur.execute("""
        INSERT INTO players
        VALUES(?,?,?,?,?)
        """, (
            int(p["player_id"]),
            str(p["name"]),
            str(p["current_club_name"]),
            str(p["position"]),
            price
        ))

    con.commit()
    con.close()


# ==========================
# КЛУБЫ
# ==========================

def set_owner(user_id, club):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT owner FROM clubs WHERE name=?",
        (club,)
    )

    data = cur.fetchone()

    if data and data[0]:
        con.close()
        return False

    cur.execute(
        "UPDATE clubs SET owner=? WHERE name=?",
        (user_id, club)
    )

    cur.execute(
        "INSERT OR REPLACE INTO users VALUES(?,?)",
        (user_id, club)
    )

    con.commit()
    con.close()

    return True


def remove_team(user_id):

    con = connect()

    con.execute(
        "UPDATE clubs SET owner=NULL WHERE owner=?",
        (user_id,)
    )

    con.execute(
        "DELETE FROM users WHERE user_id=?",
        (user_id,)
    )

    con.execute(
        "DELETE FROM squads WHERE user_id=?",
        (user_id,)
    )

    con.execute(
        "DELETE FROM formations WHERE user_id=?",
        (user_id,)
    )

    con.commit()
    con.close()


def get_user_team(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT club FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()

    con.close()

    if data:
        return data[0]

    return None


def get_budget(club):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT budget FROM clubs WHERE name=?",
        (club,)
    )

    data = cur.fetchone()

    con.close()

    if data:
        return data[0]

    return 0
# ==========================
# ИГРОКИ
# ==========================

def get_all_club_players(club):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        player_id,
        name,
        position,
        club,
        price
    FROM players
    WHERE club LIKE ?
    ORDER BY price DESC
    """, (
        "%" + club + "%",
    ))

    data = cur.fetchall()

    con.close()

    return data


def get_squad(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        p.player_id,
        p.name,
        p.position,
        p.club,
        p.price
    FROM squads s
    JOIN players p
    ON s.player_id=p.player_id
    WHERE s.user_id=?
    ORDER BY p.price DESC
    """, (user_id,))

    data = cur.fetchall()

    con.close()

    return data


def squad_count(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT COUNT(*)
    FROM squads
    WHERE user_id=?
    """, (user_id,))

    count = cur.fetchone()[0]

    con.close()

    return count


def player_in_squad(user_id, player_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT 1
    FROM squads
    WHERE user_id=?
    AND player_id=?
    """, (
        user_id,
        player_id
    ))

    data = cur.fetchone()

    con.close()

    return data is not None


# ==========================
# ПОКУПКА
# ==========================

def buy_player(user_id, player_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT club FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cur.fetchone()

    if not user:
        con.close()
        return False

    club = user[0]

    cur.execute("""
    SELECT
        name,
        price
    FROM players
    WHERE player_id=?
    """, (player_id,))

    player = cur.fetchone()

    if not player:
        con.close()
        return False

    name = player[0]
    price = player[1]

    cur.execute("""
    SELECT budget
    FROM clubs
    WHERE name=?
    """, (club,))

    budget = cur.fetchone()[0]

    if budget < price:
        con.close()
        return False

    if squad_count(user_id) >= 25:
    con.close()
    return False

if player_in_squad(user_id, player_id):
    con.close()
    return False

    # Добавляем игрока
    cur.execute("""
    INSERT INTO squads
    VALUES(?,?)
    """, (
        user_id,
        player_id
    ))

    # Снимаем деньги
    cur.execute("""
    UPDATE clubs
    SET budget = budget - ?
    WHERE name=?
    """, (
        price,
        club
    ))

    # История трансферов
    cur.execute("""
    INSERT INTO transfers
    (
        user_id,
        player_id,
        player_name,
        price,
        action,
        date
    )
    VALUES(?,?,?,?,?,?)
    """, (
        user_id,
        player_id,
        name,
        price,
        "Покупка",
        datetime.now().strftime("%d.%m.%Y %H:%M")
    ))

    con.commit()
    con.close()

    return True
# ==========================
# ПРОДАЖА ИГРОКА
# ==========================

def sell_player(user_id, player_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        p.name,
        p.price
    FROM players p
    JOIN squads s
    ON p.player_id=s.player_id
    WHERE s.user_id=?
    AND p.player_id=?
    """, (
        user_id,
        player_id
    ))

    player = cur.fetchone()

    if not player:
        con.close()
        return False

    name = player[0]
    price = player[1]

    cur.execute("""
    DELETE FROM squads
    WHERE user_id=?
    AND player_id=?
    """, (
        user_id,
        player_id
    ))

    cur.execute("""
    UPDATE clubs
    SET budget=budget+?
    WHERE owner=?
    """, (
        price,
        user_id
    ))

    cur.execute("""
    INSERT INTO transfers
    (
        user_id,
        player_id,
        player_name,
        price,
        action,
        date
    )
    VALUES(?,?,?,?,?,?)
    """, (
        user_id,
        player_id,
        name,
        price,
        "Продажа",
        datetime.now().strftime("%d.%m.%Y %H:%M")
    ))

    con.commit()
    con.close()

    return True


# ==========================
# ТОП ИГРОКОВ
# ==========================

def top_players():

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT *
    FROM players
    ORDER BY price DESC
    LIMIT 20
    """)

    data = cur.fetchall()

    con.close()

    return data


# ==========================
# ПОИСК ИГРОКА
# ==========================

def search_player(text):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT *
    FROM players
    WHERE name LIKE ?
    ORDER BY price DESC
    LIMIT 30
    """, (
        "%" + text + "%",
    ))

    data = cur.fetchall()

    con.close()

    return data


# ==========================
# ВСЕ ТРАНСФЕРЫ
# ==========================

def get_transfers():

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT *
    FROM transfers
    ORDER BY id DESC
    LIMIT 200
    """)

    data = cur.fetchall()

    con.close()

    return data


# ==========================
# ВСЕ СОСТАВЫ
# ==========================

def get_all_squads():

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        s.user_id,
        u.club,
        p.name,
        p.position,
        p.price
    FROM squads s
    JOIN users u
    ON s.user_id=u.user_id
    JOIN players p
    ON s.player_id=p.player_id
    ORDER BY u.club, p.price DESC
    """)

    data = cur.fetchall()

    con.close()

    return data


# ==========================
# ТАКТИКА
# ==========================

def set_formation(user_id, formation):

    con = connect()

    con.execute("""
    INSERT OR REPLACE INTO formations
    VALUES(?,?)
    """, (
        user_id,
        formation
    ))

    con.commit()
    con.close()


def get_formation(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT formation
    FROM formations
    WHERE user_id=?
    """, (
        user_id,
    ))

    data = cur.fetchone()

    con.close()

    if data:
        return data[0]

    return "Не выбрана"


# ==========================
# ИНФОРМАЦИЯ О КЛУБЕ
# ==========================

def get_club_info(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        u.club,
        c.budget
    FROM users u
    JOIN clubs c
    ON u.club=c.name
    WHERE u.user_id=?
    """, (
        user_id,
    ))

    data = cur.fetchone()

    con.close()

    return data


# ==========================
# СПИСОК КЛУБОВ
# ==========================

def get_all_clubs():

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT
        name,
        budget,
        owner
    FROM clubs
    ORDER BY name
    """)

    data = cur.fetchall()

    con.close()

    return data


# ==========================
# СБРОС БАЗЫ
# ==========================

def reset_database():

    con = connect()
    cur = con.cursor()

    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM squads")
    cur.execute("DELETE FROM transfers")
    cur.execute("DELETE FROM formations")

    cur.execute("""
    UPDATE clubs
    SET owner=NULL
    """)

    con.commit()
    con.close()


# ==========================
# ФОРМАТ ЦЕНЫ
# ==========================

def format_price(price):

    return f"{int(price):,}".replace(",", " ") + " €"
