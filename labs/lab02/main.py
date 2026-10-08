import sys
from pathlib import Path

# Додаємо корінь проєкту (cybersecurity-python-labs) до шляхів пошуку модулів Python
# Це дозволяє натискати на трикутник "Play" у VS Code із будь-якої папки
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from labs.lab02.task1 import Admin, AuditLog, User, UserAccount
from labs.lab02.task2 import analyze_activity


def main() -> None:
    print("=== TASK 1: Перевірка OOP моделей ===")

    # Створення користувача та налаштування пароля
    user = User(username="j_smith", email="j_smith@example.com")
    user.set_password("SecurePass123!")

    # Створення адміністратора та надання прав
    admin = Admin(username="admin_user", email="admin@example.com")
    admin.grant_permission("READ_LOGS")
    admin.grant_permission("DELETE_LOGS")
    print(f"Створено об'єкт користувача: {user}")
    print(f"Створено об'єкт адміна: {admin}")

    # Тестування авторизації та сесії
    audit = AuditLog()
    account = UserAccount(user=user, audit_log=audit)

    login_success = account.login("j_smith", "SecurePass123!", "192.168.1.105")
    print(f"Спроба входу j_smith: {'Успішна' if login_success else 'Невдала'}")
    print(f"Статус автентифікації: {account.is_authenticated()}")

    account.logout()
    print(f"Статус після виходу (logout): {account.is_authenticated()}")

    print("\n=== TASK 2: Аналіз логів активності ===")
    log_path = ROOT_DIR / "labs" / "lab02" / "data" / "data_v07" / "activity.csv"

    if log_path.exists():
        report = analyze_activity(log_path)
        print(f"\nЗагалом опрацьовано записів: {report['total_records']}")
        print(f"Знайдено аномалій позаробочого часу: {len(report['off_hours_alerts'])}")
        print(
            f"Знайдено аномалій масового скачування: {len(report['mass_download_alerts'])}"
        )
    else:
        print(f"Помилка: Файл логів не знайдено за шляхом {log_path}")


if __name__ == "__main__":
    main()
