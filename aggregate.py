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
formatter = ColoredFormatter(LOGFORMAT,log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	},datefmt='%Y-%m-%d %H:%M:%S')
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
    last_name TEXT,
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

def get_fencer(name, lname=None):
    if lname:
        full_cursor.execute(f"SELECT * FROM fencers WHERE last_name=\"{lname}\"")
        return full_cursor.fetchone()
    full_cursor.execute(f"SELECT * FROM fencers WHERE name=\"{name}\"")
    return full_cursor.fetchone()

def analyze_db(file):
    log.info(f"Analyzing {file}")
    conn = sqlite3.connect(file)
    c = conn.cursor()

    log.info("Connected to fencers database")
    total, not_in = 0, 0
    for fencer in c.execute("SELECT * FROM fencers"):
        total += 1
        id_, name, v, vom, ts, tr, i, ms, ma = fencer
        prev_row = get_fencer(name)
        if not prev_row:
            db_fencer = find_fencer(name)
            if not db_fencer:
                not_in += 1
                log.warning(f"Fencer {name} not found in members.csv")
                db_fencer = defaultdict(str)
            full_cursor.execute("INSERT INTO fencers VALUES (?,?,?,?,?,?,?,?,?)", (db_fencer["Member #"], name, name.split()[0].upper(),
                                db_fencer["Birthdate"], db_fencer["Club 1 Name"], ','.join([db_fencer[i] for i in ("Saber", "Epee", "Foil")]),
                                db_fencer["Representing Country"],'',''))
            prev_row = get_fencer(name)
        *_, tournaments, stats, _ = prev_row
        full_cursor.execute("UPDATE fencers SET tournaments = ?, stats = ? WHERE name=\"{name}\"",
                           (tournaments+":"+file.split(".")[0], stats+":"+','.join([v, vom, ts, tr, i, ms, ma])))
    full_connection.commit()
    log.debug(f"Could not find data on {not_in} fencers out of {total} total. ({not_in/total})")
    log.info("Connected to games database")
    total, not_in1, not_in2 = 0, 0, 0
    for game in c.execute("SELECT * FROM games"):
        total += 1
        id_, p1, p2, score, round_, winner = game
        if p2[0].isdigit():
            score, p2 = p2, score

        if p1 != "- BYE -":
            p1_row = get_fencer(p1, lname=p1.split()[0])
            if not p1_row:
                not_in1 += 1
                log.error(f"Fencer p1-{p1} not found in fencers")
            else:
                *_, m1 = p1_row
                full_cursor.execute("UPDATE fencers SET matches = ? WHERE name=\"{p1}\"", [m1+f"{p1}/{score}/{1 if winner == p1 else 0}"])

        if p2 != "- BYE -":
            p2_row = get_fencer(p2, lname=p2.split()[0])
            if not p2_row:
                not_in2 += 1
                log.error(f"Fencer p2-{p2} not found in fencers")
            else:
                *_, m2 = p2_row
                full_cursor.execute("UPDATE fencers SET matches = ? WHERE name=\"{p2}\"", [m2+f"{p2}/{score}/{1 if winner == p2 else 0}"])
    if not_in1 or not_in2:
        log.debug(f"Could not find data on {not_in1}+{not_in2}={not_in1+not_in2} fencers out of {total} total. ({(not_in1+not_in2)/(total*2)})")
    conn.commit()
    conn.close()
    full_connection.commit()

if __name__ == "__main__":
    _init_cursor()
    for file in os.listdir("dbs/"):
        if not file.endswith(".db") or file.startswith("agg"): continue
        analyze_db("dbs/"+file)
    full_connection.commit()
    full_connection.close()
