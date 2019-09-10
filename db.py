import sqlite3
import os

import scrape

conn = sqlite3.connect("fencing.db")
c = conn.cursor() # get cursor to file

def init_file():
    c.execute("DROP TABLE fencers")
    c.execute("DROP TABLE games")
    c.execute("""CREATE TABLE fencers (
    id int,
    name TEXT,
    victories int,
    victories_over_matches float,
    touches_scored int,
    touches_received int,
    indicator int,
    match_scores TEXT,
    match_against TEXT
);""")
    c.execute("""CREATE TABLE games (
    id int,
    p1 TEXT,
    p2 TEXT,
    score TEXT,
    round TEXT
);""")

init_file()

for event in scrape.get_events():
    for (pools, tableaus) in scrape.scrape_data(event):
        c.executemany('INSERT INTO fencers VALUES (?,?,?,?,?,?,?,?,?)', pools)
        c.executemany('INSERT INTO games VALUES (?,?,?,?,?)', tableaus)

conn.commit()
conn.close()
