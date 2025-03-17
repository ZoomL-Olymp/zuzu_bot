import sqlite3

DATABASE_NAME = "data/zuzu_bot.db"  # Path to the database file


def init_db(conn=None):
    """Creates the database and table if they don't exist."""
    if conn is None:
        conn = sqlite3.connect(DATABASE_NAME)  # Connect if no connection provided
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        )
    """)
    conn.commit()
    if conn is None: #close if we just opened
       conn.close()



def save_website_data(websites_data, conn=None):
    """Saves website data to the database."""
    if conn is None:
        conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.executemany("INSERT INTO websites (title, url, xpath) VALUES (?, ?, ?)",
                       [(data['title'], data['url'], data['xpath']) for data in websites_data])
    conn.commit()
    if conn is None:
        conn.close()

def get_all_websites(conn=None):
    """Retrieves all websites from the database."""
    if conn is None:
        conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, url, xpath FROM websites")
    columns = [col[0] for col in cursor.description]  # Get column names
    return [dict(zip(columns, row)) for row in cursor.fetchall()] # Return list of dicts