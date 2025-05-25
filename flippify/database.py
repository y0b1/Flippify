import sqlite3

class DatabaseManager:
    def __init__(self, db_name="flippify.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                source_price REAL,
                sold_price REAL,
                date TEXT
            )
        """)
        self.conn.commit()

    def insert_item(self, name, source_price, sold_price, date):
        self.cursor.execute(
            "SELECT 1 FROM items WHERE name=? AND source_price=? AND sold_price=? AND date=?",
            (name, source_price, sold_price, date)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO items (name, source_price, sold_price, date) VALUES (?, ?, ?, ?)",
                (name, source_price, sold_price, date)
            )
            self.conn.commit()

    def fetch_items(self):
        self.cursor.execute("SELECT name, source_price, sold_price, date FROM items ORDER BY id DESC")
        return self.cursor.fetchall()

    def delete_all_items(self):
        self.cursor.execute("DELETE FROM items")
        self.conn.commit()

    def delete_item(self, name, source_price, sold_price, date):
        self.cursor.execute(
            "SELECT id FROM items WHERE name=? AND source_price=? AND sold_price=? AND date=? LIMIT 1",
            (name, source_price, sold_price, date)
        )
        result = self.cursor.fetchone()
        if result:
            item_id = result[0]
            self.cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
            self.conn.commit()
