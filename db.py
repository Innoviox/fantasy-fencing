import sqlite3
import os

import scrape

conn = sqlite3.connect("fencing.db")
c = conn.cursor() # get cursor to file

def init_file():
    c.execute("DROP TABLE fencers")
    c.execute("""CREATE TABLE fencers (
    id int,
    name TEXT,
    victories int,
    victories_over_matches float,
    touches_scored int,
    touches_received int,
    indicator int
);""")

init_file()

for (pools, tableaus) in map(scrape.scrape_data, scrape.get_events()):
    c.executemany('INSERT INTO fencers VALUES (?,?,?,?,?,?,?)', pools)

conn.commit()
conn.close()
