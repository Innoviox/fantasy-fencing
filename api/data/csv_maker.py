import sqlite3, csv, os

with open("rankings.csv", "w") as f:
    fieldnames=['Name', 'Pool 1', 'Pool 2', 'Final']
    
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()

    
    for file in reversed(os.listdir("dbs/")):
        print("Reading", file)
        try:
            conn = sqlite3.connect('dbs/'+file)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM rankings")

            for row in cursor.fetchall():
                w.writerow(dict(zip(fieldnames, row)))
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            print("no rankings")
