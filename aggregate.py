import sqlite3
import csv
import os
from collections import defaultdict
import logging

# set up logging
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
from colorlog import ColoredFormatter
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT,datefmt='%Y-%m-%d %H:%M:%S')
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


full_connection = sqlite3.connect("dbs/aggregated.db")
full_cursor = full_connection.cursor()
        
def _init_cursor():
    try:
        full_cursor.execute("DROP TABLE fencers;")
    except sqlite3.OperationalError:
        pass

    full_cursor.execute("""CREATE TABLE fencers (
    id int,
    name TEXT,
    birthdate int,
    club TEXT
    ratings TEXT,
    country TEXT,
    tournaments TEXT DEFAULT '',
    stats TEXT DEFAULT '',
    matches TEXT DEFAULT ''
);""")

def find_fencer(name):
    csv_reader = csv.DictReader(open("dbs/members.csv"))
    last, first, *initial = name.split()
    
    for row in csv_reader:
        if row['Last Name'].upper() == last.upper() and first.upper() in row['First Name'].upper(): # to cover nicknames
            return row

def get_fencer(name):
    full_cursor.execute(f"SELECT * FROM fencers WHERE name=\"{name}\"")
    return full_cursor.fetchone()

def analyze_db(file):
    log.info(f"Analyzing {file}")
    conn = sqlite3.connect(file)
    c = conn.cursor()

    log.info("Connected to fencers database")
    for fencer in c.execute("SELECT * FROM fencers"):
        id_, name, v, vom, ts, tr, i, ms, ma = fencer
        prev_row = get_fencer(name)
        if not prev_row:
            db_fencer = find_fencer(name)
            if not db_fencer:
                log.warning(f"Fencer {name} not found in members.csv")
                db_fencer = defaultdict(str)
            full_cursor.execute("INSERT INTO fencers VALUES (?,?,?,?,?,?,?,?)", (db_fencer["Member #"], name,
                                db_fencer["Birthdate"], db_fencer["Club 1 Name"], ','.join([db_fencer[i] for i in ("Saber", "Epee", "Foil")]),
                                db_fencer["Representing Country"],'',''))
            prev_row = get_fencer(name)
        *_, tournaments, stats, _ = prev_row
        full_cursor.execute("UPDATE fencers SET tournaments = ?, stats = ? WHERE name=\"{name}\"",
                           (tournaments+":"+file.split(".")[0], stats+":"+','.join([v, vom, ts, tr, i, ms, ma])))

    log.info("Connected to games database")
    for game in c.execute("SELECT * FROM games"):
        id_, p1, p2, score, round_, winner = game
        
        p1_row = get_fencer(p1)
        *_, m1 = p1_row
        full_cursor.execute("UPDATE fencers SET matches = ? WHERE name=\"{p1}\"", (m1+f"{p2}/{score}/{1 if winner == p1 else 0}"))

        p2_row = get_fencer(p2)
        *_, m2 = p2_row
        full_cursor.execute("UPDATE fencers SET matches = ? WHERE name=\"{p2}\"", (m2+f"{p2}/{score}/{1 if winner == p2 else 0}"))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    _init_cursor()
    for file in os.listdir("dbs/"):
        if not file.endswith(".db"): continue
        analyze_db("dbs/"+file)
    full_connection.comit()
    full_connection.close()
