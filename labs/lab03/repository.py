import sqlite3
from contextlib import closing

from labs.lab03.database import get_connection


def create_category(name: str) -> dict:
    with closing(get_connection()) as conn:
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)", (name,)
                )
                category_id = cursor.lastrowid
            return {"id": category_id, "name": name}
        except sqlite3.IntegrityError:
            raise


def get_categories() -> list[dict]:
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT id, name FROM categories ORDER BY id").fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]


def delete_empty_category(category_id: int) -> bool:
    with closing(get_connection()) as conn:
        try:
            with conn:
                row = conn.execute(
                    "SELECT id FROM categories WHERE id = ?", (category_id,)
                ).fetchone()

                if row is None:
                    return False

                count = conn.execute(
                    "SELECT COUNT(*) FROM records WHERE category_id = ?",
                    (category_id,),
                ).fetchone()[0]

                if count:
                    raise ValueError("Категорія містить записи")

                conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return True
        except sqlite3.Error:
            raise


def get_record_by_id(record_id: int) -> dict | None:
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id,
                   c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON c.id = r.category_id
            WHERE r.id = ?
            """,
            (record_id,),
        ).fetchone()
        return dict(row) if row else None


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    query = """
        SELECT r.id, r.code, r.title, r.category_id,
               c.name AS category_name, r.value, r.status
        FROM records r
        JOIN categories c ON c.id = r.category_id
        WHERE 1 = 1
    """
    params = []

    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)
    if status is not None:
        query += " AND r.status = ?"
        params.append(status)
    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)
    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)

    query += " ORDER BY r.id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def create_record(
    code: str, title: str, category_id: int, value: float, status: str
) -> dict:
    with closing(get_connection()) as conn:
        try:
            with conn:
                category = conn.execute(
                    "SELECT name FROM categories WHERE id = ?", (category_id,)
                ).fetchone()

                if category is None:
                    raise ValueError("Категорію не знайдено")

                cursor = conn.execute(
                    """
                    INSERT INTO records
                    (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (code, title, category_id, value, status),
                )
                record_id = cursor.lastrowid

            return {
                "id": record_id,
                "code": code,
                "title": title,
                "category_id": category_id,
                "category_name": category[0],
                "value": value,
                "status": status,
            }
        except sqlite3.Error:
            raise


def update_record(
    record_id: int,
    code: str,
    title: str,
    category_id: int,
    value: float,
    status: str,
) -> dict:
    with closing(get_connection()) as conn:
        with conn:
            exists = conn.execute(
                "SELECT id FROM records WHERE id = ?", (record_id,)
            ).fetchone()

            if exists is None:
                raise KeyError("Запис не знайдено")

            category = conn.execute(
                "SELECT name FROM categories WHERE id = ?", (category_id,)
            ).fetchone()

            if category is None:
                raise ValueError("Категорію не знайдено")

            conn.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (code, title, category_id, value, status, record_id),
            )

        return {
            "id": record_id,
            "code": code,
            "title": title,
            "category_id": category_id,
            "category_name": category[0],
            "value": value,
            "status": status,
        }


def delete_record(record_id: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0


def batch_create_records(records: list[dict]) -> list[dict]:
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row

        codes = [item["code"] for item in records]
        if len(codes) != len(set(codes)):
            raise sqlite3.IntegrityError("Дублікат коду в пакеті")

        category_ids = list({item["category_id"] for item in records})
        placeholders = ",".join("?" for _ in category_ids)
        rows = conn.execute(
            f"SELECT id, name FROM categories WHERE id IN ({placeholders})",
            category_ids,
        ).fetchall()
        categories = {row["id"]: row["name"] for row in rows}

        for item in records:
            if item["category_id"] not in categories:
                raise ValueError("Категорію не знайдено")

        result = []

        with conn:
            for item in records:
                cursor = conn.execute(
                    """
                    INSERT INTO records
                    (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        item["code"],
                        item["title"],
                        item["category_id"],
                        item["value"],
                        item["status"],
                    ),
                )
                result.append(
                    {
                        **item,
                        "id": cursor.lastrowid,
                        "category_name": categories[item["category_id"]],
                    }
                )

        return result
