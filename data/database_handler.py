import os
import sqlite3


class DatabaseHandler:
    def __init__(self, database_name: str):
        self.con = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}/{database_name}")
        self.con.row_factory = sqlite3.Row

    def get_songs(self) -> list:
        cursor = self.con.cursor()
        query = "SELECT * FROM song;"
        cursor.execute(query)
        result = cursor.fetchall()
        return [dict(res) for res in result]

    def get_song_by_name(self, name: str):
        cursor = self.con.cursor()
        query = "SELECT * FROM song WHERE name = ?;"
        cursor.execute(query, (name,))
        result = cursor.fetchall()
        return dict(result[0])
