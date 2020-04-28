import tkinter as tk
from tkinter import ttk
import sqlite3 as sql

import click

class Database(tk.Tk):
    def __init__(self, cursor):
        tk.Tk.__init__(self)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

        self.trees = []

        for idx, table in enumerate(cursor.fetchall()):
            self.trees.append(ttk.Treeview(self))
        
            self.trees[-1].insert('', 'end', text=table)

            tk.Button(self, text=table, command=self.show(idx)).grid(row=0, column=idx)
            self.trees[-1].grid(row=1)
        
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
