"""Завдання 3."""

import csv
import datetime
import hashlib
import json
import sys
from functools import wraps
from pathlib import Path

# Додавання кореня проєкту до sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from shared.student import (
    GROUP_NAME,
    STUDENT_NAME,
    VARIANT_NUMBER,
)

# Константи та файлові шляхи
MIN_PASSWORD_LENGTH = 15
DATA_DIR = Path(__file__).resolve().parent / "data"
CSV_FILE = DATA_DIR / "users.csv"
LOG_FILE = DATA_DIR / "log.json"

# Глобальна база даних для зберігання зчитаних користувачів
users_db: list[dict[str, str]] = []


class ValidationError(Exception):
    """Виняток для помилки валідації пароля."""


def generate_hash(password: str, salt: str = "00000") -> str:
    """Генерує SHA-384 хеш від конкатенації пароля та солі."""
    if not password:
        raise ValueError("Пароль не може бути порожнім")

    if not salt:
        raise ValueError("Сіль не може бути порожньою")

    if len(password) < MIN_PASSWORD_LENGTH:
        msg = (
            f"Пароль повинен містити щонайменше {MIN_PASSWORD_LENGTH} символів"
        )
        raise ValidationError(msg)

    salted_password = (password + salt).encode("utf-8")
    return hashlib.sha384(salted_password).hexdigest()


def create_user(username: str, password: str) -> tuple[str, str]:
    """Створює кортеж (username, hash_value) з персональною сіллю."""
    salt = f"{VARIANT_NUMBER:05d}"
    hash_value = generate_hash(password, salt)
    return username, hash_value


def create_users(
    users_list: tuple[tuple[str, str], ...] | list[tuple[str, str]],
) -> None:
    """Створює базу користувачів та записує її у CSV-файл."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    registered_users = []

    for username, password in users_list:
        try:
            user = create_user(username, password)
            registered_users.append(user)
        except ValidationError as error:
            print(f"[ПОМИЛКА ВАЛІДАЦІЇ] Користувач '{username}': {error}")
        except ValueError as error:
            print(f"[ПОМИЛКА ЗНАЧЕННЯ] Користувач '{username}': {error}")
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password_hash"])
            writer.writerows(registered_users)

        print(f"CSV-базу успішно створено: {CSV_FILE}")

    except PermissionError as error:
        print(f"[PERMISSION ERROR]: {error}")
    except OSError as error:
        print(f"[IO ERROR]: {error}")


def read_users() -> list[dict[str, str]]:
    """Зчитує користувачів із CSV-файлу у список словників."""
    users = []
    try:
        with open(CSV_FILE, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError as error:
        print(f"[FILE NOT FOUND]: {error}")
    except PermissionError as error:
        print(f"[PERMISSION ERROR]: {error}")
    except OSError as error:
        print(f"[IO ERROR]: {error}")

    return users


def print_users_table(users: list[dict[str, str]]) -> None:
    """Виводить базу користувачів у структурованій таблиці."""
    print("\n" + "=" * 65)
    print("БАЗА КОРИСТУВАЧІВ")
    print("=" * 65)
    print(f"{'Логін':<15} | {'SHA-384 хеш (перші 35 симв.)'}")
    print("-" * 65)
    for user in users:
        print(f"{user['username']:<15} | {user['password_hash'][:35]}...")
    print("=" * 65)


def log_event(func):
    """Декоратор для логування спроб входу у файл JSON."""

    @wraps(func)
    def wrapper(username: str, password: str, *args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_status = "failure"

        try:
            result = func(username, password, *args, **kwargs)
            if result:
                result_status = "success"
            return result
        finally:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            event_data = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": timestamp,
                "args": [],
                "kwargs": {},
            }

            logs = []
            if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
                try:
                    with open(LOG_FILE, encoding="utf-8") as file:
                        logs = json.load(file)
                except json.JSONDecodeError:
                    logs = []

            if not isinstance(logs, list):
                logs = []

            logs.append(event_data)
            with open(LOG_FILE, "w", encoding="utf-8") as file:
                json.dump(logs, file, indent=4, ensure_ascii=False)

    return wrapper


@log_event
def login(username: str, password: str) -> bool:
    """Перевіряє логін і пароль користувача."""
    try:
        if not username or not password:
            raise ValueError("Логін і пароль не можуть бути порожніми")

        salt = f"{VARIANT_NUMBER:05d}"
        entered_hash = generate_hash(password, salt)

        for user in users_db:
            if user["username"] == username:
                return user["password_hash"] == entered_hash

    except ValidationError as error:
        print(f"[VALIDATION ERROR]: {error}")
        return False
    except ValueError as error:
        print(f"[VALUE ERROR]: {error}")
        return False

    return False


def main() -> None:
    """Головна функція виконання Завдання 3."""
    print("=" * 65)
    info_str = (
        f"Студентка: {STUDENT_NAME} | "
        f"Група: {GROUP_NAME} | "
        f"Варіант: {VARIANT_NUMBER}"
    )
    print(info_str)
    print("=" * 65)

    users_to_register = (
        ("admin", "SuperSecurePass123!"),
        ("user1", "ComplexPassword789#"),
        ("analyst", "VeryLongSecretPass1"),
        ("tech", "MonitoringAccess2023!"),
        ("guest", "GuestSecurePassword123!"),
        ("lead", "IncidentCommander999!"),
        ("audit", "AuditSystemPass321#"),
        ("dev", "SoftwareDevPass456!"),
        ("manager", "ManagementSecurity777!"),
        ("support", "SupportServicePass888#"),
    )

    print("\n[1] Створення бази користувачів...")
    create_users(users_to_register)
    print("\n[2] Зчитування CSV-бази...")
    loaded_users = read_users()
    users_db.clear()
    users_db.extend(loaded_users)
    print_users_table(users_db)

    print("\n[3] Тестування автентифікації...")
    res1 = login("admin", "SuperSecurePass123!")
    status1 = "УСПІХ" if res1 else "НЕВДАЧА"
    print(f"1. admin (правильний пароль): {status1}")

    res2 = login("admin", "WrongPassword12345!")
    status2 = "УСПІХ" if res2 else "НЕВДАЧА"
    print(f"2. admin (неправильний пароль): {status2}")

    res3 = login("unknown", "SomePassword12345!")
    status3 = "УСПІХ" if res3 else "НЕВДАЧА"
    print(f"3. Неіснуючий користувач: {status3}")

    print(f"\nСпроби авторизації успішно записано у {LOG_FILE}")


if __name__ == "__main__":
    main()
