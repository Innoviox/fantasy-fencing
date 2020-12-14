import sqlite3
import pdftotext
import csv

from data.logs import log


def init_file(c):
    try:
        c.execute("DROP TABLE fencers")
    except sqlite3.OperationalError:
        print("attempt to reinit noninited file")
    c.execute("""CREATE TABLE fencers (
    id int,
    member_id int,
    name TEXT,
    birthdate int,
    
    rating TEXT,
    ranking int,
    
    matches int,
    wins    int
);""")


def name(row):
    m = row['Middle Name'] or ''
    if m:
        m = ' ' + m[0]

    s = row['Suffix'] or ''
    if s:
        s = ' ' + s

    return f"{row['Last Name'].title()}{s}, {row['First Name'].title()}"  # {m}


log.debug(f"Writing fencer database")
conn = sqlite3.connect(f"dbs/fencers.db")
c = conn.cursor()
init_file(c)

with open("members.csv") as members:
    id = 0
    for row in csv.DictReader(members):
        c.execute("INSERT INTO fencers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id,
                                                                          row['Member #'],
                                                                          name(row),
                                                                          row['Birthdate'],
                                                                          row['Epee'],
                                                                          '',
                                                                          0,
                                                                          0))
        id += 1

with open("ME Sr R 2020 03 08.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

for page in pdf:
    for line in page.split("\n"):
        l = line.split()

        if len(l) >= 14:
            r = l[0].strip('T')
            if r.isnumeric():
                yr_idx = next(i for (i, j) in enumerate(l) if len(j) == 4 and j.isnumeric())
                name = ' '.join(l[1:yr_idx]).strip('# ')
                if len(name.split()[-1]) == 1:  # remove middle initial
                    name = name[:-2]
                c.execute("UPDATE fencers SET ranking = ? WHERE name = ? and birthdate = ?",
                          (int(r), name, int(l[yr_idx])))

conn.commit()
conn.close()
