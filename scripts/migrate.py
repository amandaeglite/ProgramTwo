import sqlite3
import pathlib

MIGRACIJA_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"


def migrate(db_path="mythology.db"):
    con = sqlite3.connect(db_path)
    con.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)"
    )
    done = {row[0] for row in con.execute("SELECT name FROM schema_migrations")}

    for sql_file in sorted(MIGRACIJA_DIR.glob("*.sql")):
        if sql_file.name not in done:
            print(f"Applying {sql_file.name}")
            con.executescript(sql_file.read_text(encoding="utf-8-sig"))
            con.execute(
                "INSERT INTO schema_migrations (name) VALUES (?)", (sql_file.name,)
            )
            con.commit()

    con.close()


if __name__ == "__main__":
    migrate()