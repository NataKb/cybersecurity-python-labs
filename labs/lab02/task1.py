import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

SESSION_TIMEOUT_SEC = 900


# ПРАВКА 1: Додано класи винятків (ексепти)
class AuthError(Exception):
    """Базовий клас винятків для помилок аутентифікації."""


class InvalidEmailError(ValueError, AuthError):
    """Виникає при спробі встановити некоректний email."""


class User:
    """Базовий клас користувача з інкапсуляцією та хешуванням паролів."""

    def __init__(self, username: str, email: str, role: str = "user") -> None:
        self.username = username
        self.email = email
        self.role = role
        self.active = True
        self.__password_salt = os.urandom(16)
        self.__password_hash = b""

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        pattern = r"^[a-zA-Z][a-zA-Z0-9._%+-]{2,63}@[\w\.-]+\.\w+$"
        if not re.match(pattern, value):
            # ПРАВКА 2: Перевірка неправильного email через raise InvalidEmailError
            raise InvalidEmailError(f"Некоректний формат email: {value}")
        self._email = value

    def set_password(self, password: str) -> None:
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, 100000
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_hash:
            return False
        calculated = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, 100000
        )
        return hmac.compare_digest(self.__password_hash, calculated)

    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status='{status}')"


class Admin(User):
    """Клас адміністратора, що розширює User правами доступу."""

    def __init__(
        self,
        username: str,
        email: str,
        permissions: list[str] | set[str] | None = None,
    ) -> None:
        super().__init__(username, email, role="admin")
        self.permissions: set[str] = set(permissions) if permissions else set()

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms = ", ".join(sorted(self.permissions))
        return f"{base_str} [Permissions: {perms}]"


class Session:
    """Клас сесії з перевіркою часу активності в UTC."""

    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = self.login_time

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Таймаут повинен бути позитивним числом.")
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed <= timeout_sec


@dataclass
class LogEntry:
    """Запис у журналі аудиту."""

    timestamp: str
    username: str
    action: str


class AuditLog:
    """Журнал подій безпеки."""

    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    def add_log(self, username: str, action: str) -> None:
        now_str = datetime.now(timezone.utc).isoformat()
        self.entries.append(LogEntry(now_str, username, action))

    def show_all(self) -> None:
        for entry in self.entries:
            print(
                f"[{entry.timestamp}] User: {entry.username} | Action: {entry.action}"
            )


class UserAccount:
    """Композиційний клас зв'язування об'єктів User, Session та AuditLog."""

    SESSION_TIMEOUT_SEC = SESSION_TIMEOUT_SEC

    def __init__(
        self,
        user: User,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.user = user
        self.audit_log = audit_log if audit_log is not None else AuditLog()
        self.session: Session | None = None

    def login(self, username: str, password: str, ip: str) -> bool:
        if (
            self.user.username == username
            and self.user.active
            and self.user.check_password(password)
        ):
            self.session = Session(ip=ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True
        self.audit_log.add_log(username, "login_failure")
        return False

    def is_authenticated(self) -> bool:
        return bool(self.session and self.session.is_active(self.SESSION_TIMEOUT_SEC))

    def logout(self) -> None:
        if self.session:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str) -> Any:
        allowed = {
            "user": self.user,
            "session": self.session,
            "audit_log": self.audit_log,
        }
        # ПРАВКА 3: Обробка винятку (ексепта) KeyError
        try:
            return allowed[key]
        except KeyError:
            raise KeyError(f"Ключ '{key}' недоступний чи заборонений.")

    def __setitem__(self, key: str, value: Any) -> None:
        # ПРАВКА 4: Обробка винятку (ексепта) TypeError
        try:
            if key == "user" and isinstance(value, User):
                self.user = value
            elif key == "session" and (isinstance(value, Session) or value is None):
                self.session = value
            else:
                raise TypeError
        except TypeError:
            raise TypeError(f"Неможливо встановити значення для ключа '{key}'")


def main() -> None:
    print("=== Завдання 1: ООП та InvalidEmailError ===")

    user = User("student01", "student@example.com")
    user.set_password("password123")

    print(user)
    print("Перевірка правильного пароля:", user.check_password("password123"))
    print("Перевірка неправильного пароля:", user.check_password("wrong"))

    admin = Admin("admin01", "admin@example.com", {"read", "write"})
    print(admin)
    print("Дозвіл write:", admin.has_permission("write"))

    account = UserAccount(user)
    print("Успішний вхід:", account.login("student01", "password123", "127.0.0.1"))
    print("Автентифіковано:", account.is_authenticated())

    try:
        User("invalid", "invalid-email")
    except InvalidEmailError as error:
        print("Перехоплено виняток:", error)

    print("\nЖурнал подій:")
    account.audit_log.show_all()


if __name__ == "__main__":
    main()
