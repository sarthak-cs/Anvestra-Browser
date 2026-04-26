import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HistoryManager:
    def __init__(self, db_name="Anvestra_history.db"):
        db_path = os.path.join(BASE_DIR, db_name)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT NOT NULL,
                timestamp TEXT
            )
        """)


        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_url ON history(url)
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT NOT NULL UNIQUE,
                created_at TEXT
            )
        """)

        self.conn.commit()


    def add_entry(self, title, url):
        timestamp = datetime.now().isoformat()


        self.cursor.execute("""
            SELECT id FROM history
            WHERE url = ?
            ORDER BY id DESC
            LIMIT 1
        """, (url,))

        row = self.cursor.fetchone()

        if row:

            self.cursor.execute("""
                UPDATE history
                SET timestamp = ?
                WHERE id = ?
            """, (timestamp, row[0]))
        else:
            self.cursor.execute("""
                INSERT INTO history (title, url, timestamp)
                VALUES (?, ?, ?)
            """, (title, url, timestamp))


        self.cursor.execute("""
            DELETE FROM history
            WHERE id NOT IN (
                SELECT id FROM history
                ORDER BY id DESC
                LIMIT 1000
            )
        """)

        self.conn.commit()

    def get_history(self, limit=100):
        self.cursor.execute("""
            SELECT title, url, timestamp
            FROM history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()

    def search_urls(self, query, limit=5):
        self.cursor.execute("""
            SELECT url FROM history
            WHERE LOWER(url) LIKE LOWER(?)
            ORDER BY id DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        return [row[0] for row in self.cursor.fetchall()]
    

    def add_bookmark(self, title, url):
        timestamp = datetime.now().isoformat()
        try:
            self.cursor.execute("""
                INSERT INTO bookmarks (title, url, created_at)
                VALUES (?, ?, ?)
            """, (title, url, timestamp))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass 

    def remove_bookmark(self, url):
        self.cursor.execute("""
            DELETE FROM bookmarks WHERE url = ?
        """, (url,))
        self.conn.commit()

    def get_bookmarks(self):
        self.cursor.execute("""
            SELECT title, url FROM bookmarks
            ORDER BY id DESC
        """)
        return self.cursor.fetchall()

    def is_bookmarked(self, url):
        self.cursor.execute("""
            SELECT 1 FROM bookmarks WHERE url = ?
        """, (url,))
        return self.cursor.fetchone() is not None


    def close(self):
        self.conn.close()