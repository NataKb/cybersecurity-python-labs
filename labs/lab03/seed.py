import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"
STATUSES = {"new", "in_progress", "done"}


def validate_data(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("JSON має містити об'єкт")

    categories = data.get("categories")
    records = data.get("records")

    if not isinstance(categories, list) or not isinstance(records, list):
        raise ValueError("Потрібні масиви categories і records")

    if len(categories) != 3 or len(records) != 8:
        raise ValueError("Потрібно рівно 3 категорії та 8 записів")

    category_ids = set()
    category_names = set()

    for category in categories:
        if not isinstance(category, dict):
            raise ValueError("Некоректна категорія")

        category_id = category.get("id")
        name = category.get("name")

        if type(category_id) is not int or category_id <= 0:
            raise ValueError("ID категорії має бути додатним цілим числом")

        if not isinstance(name, str) or not 2 <= len(name.strip()) <= 40:
            raise ValueError("Некоректна назва категорії")

        if category_id in category_ids or name.strip() in category_names:
            raise ValueError("Категорії не повинні повторюватися")

        category_ids.add(category_id)
        category_names.add(name.strip())

    codes = set()

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Некоректний запис")

        code = record.get("code")
        title = record.get("title")
        category_id = record.get("category_id")
        value = record.get("value")
        record_status = record.get("status")

        if not isinstance(code, str) or not 3 <= len(code.strip()) <= 40:
            raise ValueError("Некоректний code")

        if not isinstance(title, str) or not 3 <= len(title.strip()) <= 120:
            raise ValueError("Некоректний title")

        if code.strip() in codes:
            raise ValueError("Коди записів не повинні повторюватися")
        codes.add(code.strip())

        if type(category_id) is not int or category_id not in category_ids:
            raise ValueError("Запис посилається на невідому категорію")

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError("Час має бути скінченним числом від 0")

        if record_status not in STATUSES:
            raise ValueError("Некоректний статус запису")


def seed_database() -> None:
    try:
        initialize_database()
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        validate_data(data)

        with closing(get_connection()) as conn:
            with conn:
                categories_count = conn.execute(
                    "SELECT COUNT(*) FROM categories"
                ).fetchone()[0]
                records_count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[
                    0
                ]

                if categories_count or records_count:
                    print("База вже містить дані. Змін не внесено.")
                    return

                for category in data["categories"]:
                    conn.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (category["id"], category["name"].strip()),
                    )

                for record in data["records"]:
                    conn.execute(
                        """
                        INSERT INTO records
                        (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            record["code"].strip(),
                            record["title"].strip(),
                            record["category_id"],
                            record["value"],
                            record["status"],
                        ),
                    )

        print("Додано 3 категорії та 8 записів.")

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError,
        sqlite3.Error,
    ) as error:
        print(f"Помилка заповнення: {error}. Зміни скасовано.")


if __name__ == "__main__":
    seed_database()
