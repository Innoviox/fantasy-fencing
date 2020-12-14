from sqlite3 import connect as q
c=q("dbs/aggregated.db")
for r in c.execute("SELECT * FROM fencers"):
    print(r)
