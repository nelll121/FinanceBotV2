"""CRUD service for local users storage (`data/users.json`)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Any

DATA_DIR = Path("data")
USERS_PATH = DATA_DIR / "users.json"

_storage_lock = Lock()


@dataclass(slots=True)
class UserRecord:
    """In-memory representation of a registered bot user."""

    user_id: int
    name: str
    sheets_id: str | None = None
    api_key: str | None = None
    ai_access: bool = False
    timezone: str = "Asia/Almaty"
    morning_time: str = "09:00"
    evening_time: str = "21:00"
    notifications: bool = True
    registered_at: str = date.today().isoformat()
    is_admin: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "sheets_id": self.sheets_id,
            "api_key": self.api_key,
            "ai_access": self.ai_access,
            "timezone": self.timezone,
            "morning_time": self.morning_time,
            "evening_time": self.evening_time,
            "notifications": self.notifications,
            "registered_at": self.registered_at,
            "is_admin": self.is_admin,
        }


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_PATH.exists():
        USERS_PATH.write_text("{}\n", encoding="utf-8")


def _read() -> dict[str, dict[str, Any]]:
    _ensure_storage()
    raw = USERS_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    return json.loads(raw)


def _write(data: dict[str, dict[str, Any]]) -> None:
    _ensure_storage()
    USERS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def get_all_users() -> dict[str, dict[str, Any]]:
    """Return all saved users as a dictionary keyed by Telegram user id."""
    with _storage_lock:
        return _read()


def get_user(user_id: int) -> dict[str, Any] | None:
    """Return a user payload by Telegram user id."""
    with _storage_lock:
        return _read().get(str(user_id))


def save_user(record: UserRecord) -> dict[str, dict[str, Any]]:
    """Insert or replace user record and persist storage."""
    with _storage_lock:
        users = _read()
        users[str(record.user_id)] = record.to_dict()
        _write(users)
        return users


def update_user(user_id: int, **fields: Any) -> dict[str, Any] | None:
    """Patch one or many fields for an existing user record."""
    with _storage_lock:
        users = _read()
        key = str(user_id)
        if key not in users:
            return None
        users[key].update(fields)
        _write(users)
        return users[key]


def delete_user(user_id: int) -> bool:
    """Delete user from storage. Returns True if user existed."""
    with _storage_lock:
        users = _read()
        removed = users.pop(str(user_id), None)
        if removed is None:
            return False
        _write(users)
        return True


def count_users() -> int:
    """Return number of registered users."""
    with _storage_lock:
        return len(_read())
