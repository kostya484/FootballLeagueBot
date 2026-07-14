import sqlite3
import csv
import os


DB = "league.db"


def connect():
    return sqlite3.connect(DB)



def create_database():

    con = connect()
    cur = con.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        team TEXT
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS clubs(
        name TEXT PRIMARY KEY,
        csv_name TEXT,
        budget INTEGER DEFAULT 100000000,
        owner INTEGER
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INTEGER PRIMARY KEY,
        name TEXT,
        club TEXT,
        position TEXT,
        sub_position TEXT,
        price INTEGER
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS squad(
        user_id INTEGER,
        player_id INTEGER
    )
    """)



    clubs = [
        ("Милан","AC Milan"),
        ("Интер","Inter Milan"),
        ("Ювентус","Juventus FC"),
        ("Наполи","SSC Napoli"),
        ("Рома","AS Roma"),
        ("Лацио","SS Lazio"),
        ("Аталанта","Atalanta BC"),
        ("Торино","Torino FC"),
        ("Фиорентина","ACF Fiorentina"),
        ("Болонья","Bologna FC 1909")
    ]


    for c in clubs:

        cur.execute("""
        INSERT OR IGNORE INTO clubs
        (name,csv_name)
        VALUES(?,?)
        """, c)


    con.commit()
    con.close()




def import_players():

    if not os.path.exists("players.csv"):
        print("Нет players.csv")
        return



    con = connect()
    cur = con.cursor()



    cur.execute(
        "SELECT COUNT(*) FROM players"
    )

    if cur.fetchone()[0] > 0:
        con.close()
        return



    with open(
        "players.csv",
        encoding="utf-8"
    ) as file:


        reader = csv.DictReader(file)


        for row in reader:


            try:

                price = row.get(
                    "market_value_in_eur",
                    "0"
                )

                price = (
                    price
                    .replace(",","")
                    .replace("€","")
                )

                price = int(price)


            except:

                price = 0



            try:

                pid = int(
                    row["player_id"]
                )

            except:

                continue



            cur.execute("""
            INSERT OR IGNORE INTO players
            VALUES(?,?,?,?,?,?)
            """,
            (
                pid,
                row.get("name"),
                row.get("current_club_name"),
                row.get("position"),
                row.get("sub_position"),
                price
            ))



    con.commit()
    con.close()

    print("Игроки загружены")




def set_owner(user_id, team):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT owner
    FROM clubs
    WHERE name=?
    """,
    (team,))


    result = cur.fetchone()


    if result[0] and result[0] != user_id:

        con.close()
        return False



    cur.execute("""
    INSERT OR REPLACE INTO users
    VALUES(?,?)
    """,
    (
        user_id,
        team
    ))


    cur.execute("""
    UPDATE clubs
    SET owner=?
    WHERE name=?
    """,
    (
        user_id,
        team
    ))


    con.commit()
    con.close()

    return True




def remove_team(user_id):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    UPDATE users
    SET team=NULL
    WHERE user_id=?
    """,
    (user_id,))


    cur.execute("""
    DELETE FROM squad
    WHERE user_id=?
    """,
    (user_id,))


    con.commit()
    con.close()




def get_user_team(user_id):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT team
    FROM users
    WHERE user_id=?
    """,
    (user_id,))


    result = cur.fetchone()

    con.close()


    if result:
        return result[0]

    return None




def get_budget(team):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT budget
    FROM clubs
    WHERE name=?
    """,
    (team,))


    result = cur.fetchone()

    con.close()


    if result:
        return result[0]

    return 0




def get_all_club_players(team):

    con = connect()
    cur = con.cursor()



    cur.execute("""
    SELECT 
    p.player_id,
    p.name,
    p.position,
    p.sub_position,
    p.price

    FROM players p

    JOIN clubs c
    ON p.club=c.csv_name

    WHERE c.name=?

    LIMIT 50
    """,
    (team,))


    data = cur.fetchall()

    con.close()

    return data




def add_player_to_squad(user_id, player_id):

    con = connect()
    cur = con.cursor()



    cur.execute("""
    SELECT COUNT(*)
    FROM squad
    WHERE user_id=?
    """,
    (user_id,))


    count = cur.fetchone()[0]


    if count >= 11:

        con.close()
        return False



    cur.execute("""
    SELECT *
    FROM squad
    WHERE user_id=?
    AND player_id=?
    """,
    (
        user_id,
        player_id
    ))


    if cur.fetchone():

        con.close()
        return False



    cur.execute("""
    INSERT INTO squad
    VALUES(?,?)
    """,
    (
        user_id,
        player_id
    ))


    con.commit()
    con.close()


    return True




def get_squad(user_id):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    p.player_id,
    p.name,
    p.position

    FROM players p

    JOIN squad s
    ON p.player_id=s.player_id

    WHERE s.user_id=?
    """,
    (user_id,))


    data = cur.fetchall()

    con.close()

    return data




def top_players():

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT *
    FROM players
    ORDER BY price DESC
    LIMIT 10
    """)


    data = cur.fetchall()

    con.close()

    return data




def search_player(text):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT *
    FROM players
    WHERE name LIKE ?
    LIMIT 20
    """,
    (
        "%" + text + "%",
    ))


    data = cur.fetchall()

    con.close()

    return data




def format_price(price):

    return (
        f"{price:,}"
        .replace(",", " ")
        + " €"
  )
