import sqlite3
import os

import scrape

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

def init_file(c):
    try:
        c.execute("DROP TABLE fencers")
        c.execute("DROP TABLE games")
    except sqlite3.OperationalError:
        print("attempt to reinit noninited file")
    c.execute("""CREATE TABLE fencers (
    id int,
    name TEXT,
    victories TEXT,
    victories_over_matches TEXT,
    touches_scored TEXT,
    touches_received TEXT,
    indicator TEXT,
    match_scores TEXT,
    match_against TEXT
);""")
    c.execute("""CREATE TABLE games (
    id int,
    p1 TEXT,
    p2 TEXT,
    score TEXT,
    round TEXT,
    winner TEXT
);""")

for event, event_url in scrape.get_events():
    log.debug(f"Looking at {event} -> {event_url}")
    print(event, event_url)
    conn = sqlite3.connect(f"dbs/{event}.db")
    c = conn.cursor()
    init_file(c)
    for (pools, tableaus) in scrape.scrape_data(event_url):
        c.executemany('INSERT INTO fencers VALUES (?,?,?,?,?,?,?,?,?)', pools)
        c.executemany('INSERT INTO games VALUES (?,?,?,?,?,?)', tableaus)

    conn.commit()
    conn.close()
