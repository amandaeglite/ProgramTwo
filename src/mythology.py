import sqlite3


def connect(db_path="mythology.db"):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def add_symbol(con, name, meaning=None, category=None):
    """Insert a symbol and return its new id."""
    if not name or not name.strip():
        raise ValueError("name must not be empty")
    cur = con.execute(
        "INSERT INTO mythology_symbols (name, meaning, category) VALUES (?, ?, ?)",
        (name.strip(), meaning, category),
    )
    con.commit()
    return cur.lastrowid


def get_all_symbols(con):
    return con.execute(
        "SELECT * FROM mythology_symbols ORDER BY name"
    ).fetchall()


def get_by_category(con, category):
    return con.execute(
        "SELECT * FROM mythology_symbols WHERE category = ? ORDER BY name",
        (category,),
    ).fetchall()


def search_symbols(con, text):
    """Find symbols whose name or meaning contains the text."""
    pattern = f"%{text}%"
    return con.execute(
        "SELECT * FROM mythology_symbols "
        "WHERE name LIKE ? OR meaning LIKE ? ORDER BY name",
        (pattern, pattern),
    ).fetchall()


if __name__ == "__main__":
    con = connect()
    for row in get_all_symbols(con):
        print(row["name"], "-", row["meaning"], f"[{row['category']}]")