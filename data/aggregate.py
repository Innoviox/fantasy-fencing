import sqlite3
import csv
import os
from collections import defaultdict
from data.logs import log

full_connection = sqlite3.connect("dbs/fencers.db")
full_cursor = full_connection.cursor()

def parse_name(name):
    n = ' '.join(i.title() for i in name.split()).split('(')[0].strip()
    if ',' not in n:
        n = n.split()
        n = ' '.join(n[:-1]) + ', ' + n[-1]
    return n

def get_fencer(name):
    full_cursor.execute(f"SELECT * FROM fencers WHERE name LIKE \"%{parse_name(name)}%\"")
    return full_cursor.fetchone()

def analyze_db(file):
    log.info(f"Analyzing {file}")
    conn = sqlite3.connect(file)
    c = conn.cursor()

    # log.info("Connected to fencers database")
    total, not_in = 0, 0
    for fencer in c.execute("SELECT * FROM fencers"):
        total += 1
        id_, name, v, vom, ts, tr, i, ms, ma = fencer
        prev_row = get_fencer(name)
        if not prev_row:
            not_in += 1
            # print(name)
            # log.warning(f"Fencer {name} ({parse_name(name)}) not found in members.csv")
    full_connection.commit()
    if total != 0:
        log.debug(f"Could not find data on {not_in} fencers out of {total} total. ({not_in/total})")
    else:
        log.error("No fencers.")
    log.info("Connected to games database")
    total, not_in1, not_in2 = 0, 0, 0
    for game in c.execute("SELECT * FROM games"):
        total += 1
        id_, p1, p2, score, round_, winner = game
        if p2[0].isdigit():
            score, p2 = p2, score
        l1 = p1.split()[0]
        l2 = p2.split()[0]
        w = winner.split()[0]
        if p1 != "- BYE -":
            p1_row = get_fencer(p1, lname=l1)
            if not p1_row:
                not_in1 += 1
                log.error(f"Fencer p1-{p1}-{l1} not found in fencers")
            else:
                *_, m1 = p1_row
                full_cursor.execute("UPDATE fencers SET matches = ? WHERE last_name=?", [m1+f",{l2}/{score}/{1 if w == l1 else 0}", l1])

        if p2 != "- BYE -":
            p2_row = get_fencer(p2, lname=l2)
            if not p2_row:
                not_in2 += 1
                log.error(f"Fencer p2-{p2}-{l2} not found in fencers")
            else:
                *_, m2 = p2_row
                full_cursor.execute("UPDATE fencers SET matches = ? WHERE last_name=?", [m2+f",{l1}/{score}/{1 if w == l2 else 0}", l2])
    if not_in1 or not_in2:
        log.debug(f"Could not find data on {not_in1}+{not_in2}={not_in1+not_in2} fencers out of {total} total. ({(not_in1+not_in2)/(total*2)})")
    log.info(f"Finished with {file}.")
    conn.commit()
    conn.close()
    full_connection.commit()

    return (total, not_in)

if __name__ == "__main__":
    a, b = 0, 0
    for file in sorted(os.listdir("dbs/")):
        if not file.endswith(".db") or file.startswith("agg") or file.startswith("fencers"): continue
        # try:
        t, n = analyze_db("dbs/"+file)
        a += t; b += n
        # except Exception as e:
        #     log.error(f"exception: {e}")
        # exit()

    log.debug(f"Finished; missing {b} out of {a} ({b / a})")
    full_connection.commit()
    full_connection.close()
