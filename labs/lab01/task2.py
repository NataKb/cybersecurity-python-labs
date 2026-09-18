"""Завдання 2."""

import sys
from pathlib import Path

# Додаємо шлях до кореневої папки проєкту для імпорту shared
sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

USERS = {
    "incident_commander": {
        "role": "incident_response",
        "clearance": 4,
        "department": "CSIRT",
        "active": True,
    },
    "malware_analyst": {
        "role": "malware_researcher",
        "clearance": 3,
        "department": "Research",
        "active": True,
    },
    "monitoring_tech": {
        "role": "monitoring",
        "clearance": 2,
        "department": "NOC",
        "active": True,
    },
    "customer_rep": {
        "role": "customer_service",
        "clearance": 1,
        "department": "Customer",
        "active": True,
    },
    "backup_service": {
        "role": "service_account",
        "clearance": 2,
        "department": "System",
        "active": False,
    },
}

RESOURCES = [
    ("incident_playbook", 4),
    ("malware_lab", 3),
    ("monitoring_dashboards", 2),
    ("customer_portal", 1),
    ("emergency_procedures", 4),
    ("service_desk", 1),
    ("reverse_engineering", 3),
    ("alert_systems", 2),
    ("escalation_matrix", 3),
    ("knowledge_base", 1),
]

SECURITY_LEVELS = ("Public Access", "Authorized", "Privileged", "Critical")
BLOCKED_USERS = {"backup_service", "deactivated_svc", "policy_violation"}


def check_access(username: str, resource_level: int) -> tuple[str, str]:
    """Перевіряє рівень доступу користувача до ресурсу."""
    if username not in USERS:
        return "DENY", "User not found"

    if username in BLOCKED_USERS:
        return "DENY", "User is blocked"

    user_info = USERS[username]

    if not user_info.get("active", False):
        return "DENY", "Account inactive"

    if user_info.get("clearance", 0) >= resource_level:
        return "ALLOW", ""

    return "DENY", "Insufficient clearance"


def run_task2() -> None:
    """Запускає перевірку доступу та виводить результати."""
    print("=" * 60)
    print(
        f"Студент: {STUDENT_NAME} | "
        f"Група: {GROUP_NAME} | "
        f"Варіант: {VARIANT_NUMBER}",
    )
    print("=" * 60)

    print(
        "\nСПИСОК РЕСУРСІВ СИСТЕМИ:\n"
        + f"{'Назва ресурсу':<25} | {'Числовий рівень':<15} | {'Текстовий рівень'}\n"
        + "-" * 65
    )
    for res_name, level in RESOURCES:
        print(f"{res_name:<25} | {level:<15} | {SECURITY_LEVELS[level - 1]}")

    print("\nРЕЗУЛЬТАТИ ПЕРЕВІРКИ ДОСТУПУ:")
    print("-" * 65)

    for username in USERS:
        for res_name, level in RESOURCES:
            status, reason = check_access(username, level)
            if status == "ALLOW":
                print(f"user=[{username}] resource=[{res_name}] -> ALLOW")
            else:
                print(
                    f"user=[{username}] resource=[{res_name}] -> "
                    f"DENY ({reason})",
                )


if __name__ == "__main__":
    run_task2()
