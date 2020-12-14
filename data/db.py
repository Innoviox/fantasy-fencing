import sqlite3

from data import scrape
from data.logs import log

def init_file(c):
    try:
        c.execute("DROP TABLE fencers")
        c.execute("DROP TABLE games")
        c.execute("DROP TABLE rankings")
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
    c.execute("""CREATE TABLE rankings (
        name TEXT,
        pools_1 INT,
        pools_2 INT,
        final INT
    );""")

for event, event_url in scrape.get_events():
# for event, event_url in [['2016.12-DEC-NAC', 'https://www.usfencingresults.org/results/2016-2017/./2016.12-DEC-NAC/FTEvent_2016Dec02_DV1ME.htm']]:
    log.debug(f"Looking at {event} -> {event_url}")
    # print(event, event_url)
    # input()
    conn = sqlite3.connect(f"dbs/{event}.db")
    c = conn.cursor()
    init_file(c)
    try:
        for (pools, tableaus, rankings) in scrape.scrape_data(event_url):
            c.executemany('INSERT INTO fencers VALUES (?,?,?,?,?,?,?,?,?)', pools)
            c.executemany('INSERT INTO games VALUES (?,?,?,?,?,?)', tableaus)
            c.executemany('INSERT INTO rankings VALUES (?,?,?,?)', rankings)
    except Exception as e:
        # print(e)
        log.error(e)
        raise e
    conn.commit()
    conn.close()
