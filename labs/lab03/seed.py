import json
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database():
    try:
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        categories = data["categories"]
        records = data["records"]

        if len(categories) != 3 or len(records) != 8:
            raise ValueError("Потрібно рівно 3 категорії та 8 записів")

        initialize_database()

        with closing(get_connection()) as conn:
            with conn:
                existing_categories = conn.execute(
                    "SELECT COUNT(*) FROM categories"
                ).fetchone()[0]

                existing_records = conn.execute(
                    "SELECT COUNT(*) FROM records"
                ).fetchone()[0]

                if existing_categories == 3 and existing_records == 8:
                    print("База вже містить 3 категорії та 8 записів.")
                    print("Повторне заповнення не потрібне.")
                    return

                if existing_categories or existing_records:
                    print("База вже містить дані. Нові записи не додавалися.")
                    return

                for category in categories:
                    conn.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (category["id"], category["name"]),
                    )

                for record in records:
                    conn.execute(
                        """
                        INSERT INTO records
                        (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            record["code"],
                            record["title"],
                            record["category_id"],
                            record["value"],
                            record["status"],
                        ),
                    )

        print("Базу заповнено: 3 категорії та 8 записів.")

    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        sqlite3.Error,
    ) as error:
        print(f"Помилка заповнення: {error}")


if __name__ == "__main__":
    seed_database()
