import sqlite3

DATABASE_NAME = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            playlist TEXT,
            completedVideos TEXT,
            feedbackState TEXT,
            streak INTEGER DEFAULT 0,
            progressPercent INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()