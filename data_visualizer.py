import tkinter as tk
from tkinter import ttk
import sqlite3 as sql

import click

class Database(tk.Tk):
    def __init__(self, cursor):
        tk.Tk.__init__(self)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

        self.trees = []

        tables = cursor.fetchall()

        for idx, table in enumerate(tables):
            cursor.execute(f"SELECT * from '{table[0]}'")

            cols = [d[0] for d in cursor.description]
            tree = ttk.Treeview(self, columns=cols)
            
            for col in cols:
                tree.column(col)

            for fencer in cursor.fetchall():
                tree.insert('', tk.END, values=fencer)

            self.trees.append(tree)
            tk.Button(self, text=table, command=self.show(idx)).grid(row=0, column=idx, columnspan=1)
            tree.grid(row=1, column=0, columnspan=len(tables))     
        
    def show(self, i):
        return self.trees[i].tkraise

@click.command()
@click.argument("file", type=click.File('rb'))
def visualize(file):
    conn = sql.connect(file.name)
    cursor = conn.cursor()

    # 
    Database(cursor).mainloop()
    
    conn.close()
    
if __name__ == '__main__':
    visualize()
