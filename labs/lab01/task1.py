"""Завдання 1."""

import random
import string
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

passwords = [
    "NetworkS3c!",
    "easy",
    "Firewa11@Pass",
    "anonymous",
    "Intrus10n#Detect",
    "sample",
    "Malwar3@Scan",
    "qwerty",
    "Vulnerab1l!ty",
    "common",
]

criteria = {
    "min_length": 9,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}
forbidden_passwords = {
    "easy",
    "anonymous",
    "sample",
    "qwerty",
    "common",
    "password",
}


def evaluate_password(pwd: str, all_passwords: list[str]) -> str:
    """Оцінює надійність пароля за заданими критеріями."""
    min_len = criteria["min_length"]

    if pwd in forbidden_passwords or len(pwd) < min_len:
        return "Заборонений"

    # Перевірка наявності наборів символів
    has_digit = any(char.isdigit() for char in pwd)
    has_upper = any(char.isupper() for char in pwd)
    has_lower = any(char.islower() for char in pwd)
    has_special = any(char in string.punctuation for char in pwd)

    crit_matches = sum([has_digit, has_upper, has_lower, has_special])
    all_criteria_met = has_digit and has_upper and has_special and has_lower

    if (
        all_criteria_met
        and len(pwd) >= min_len + 4
        and all_passwords.count(pwd) == 1
    ):
        return "Дуже сильний"

    if all_criteria_met and len(pwd) < min_len + 4:
        return "Сильний"

    if crit_matches == 1:
        return "Слабкий"

    return "Середній"


def run_task1() -> None:
    """Головна функція для запуску Завдання 1."""
    print("=" * 60)
    print(
        f"Студентка: {STUDENT_NAME} | "
        f"Група: {GROUP_NAME} | "
        f"Варіант: {VARIANT_NUMBER}",
    )
    print("=" * 60)

    # Імітація повторного використання: вибір 3 випадкових індексів
    task_passwords = passwords.copy()
    random_indices = random.sample(range(len(task_passwords)), 3)
    duplicates = [task_passwords[i] for i in random_indices]
    task_passwords.extend(duplicates)

    print(f"Додано дублікати паролів: {duplicates}\n")

    # Вивід результатів аналізу у вигляді таблиці
    print(f"{'Пароль':<20} | {'Довжина':<8} | {'Статус надійності'}")
    print("-" * 55)

    for pwd in task_passwords:
        status = evaluate_password(pwd, task_passwords)
        print(f"{pwd:<20} | {len(pwd):<8} | {status}")


if __name__ == "__main__":
    run_task1()
