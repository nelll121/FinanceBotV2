"""Startup and help handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import ADMIN_USER_ID, TIMEZONE
from bot.keyboards import build_main_keyboard
from bot.services.users import UserRecord, get_user, save_user

router = Router(name="start")


def _is_admin(user_id: int) -> bool:
    if not ADMIN_USER_ID:
        return False
    return str(user_id) == str(ADMIN_USER_ID)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Register user and show main menu."""
    tg_user = message.from_user
    if tg_user is None:
        return

    existing = get_user(tg_user.id)
    if existing is None:
        record = UserRecord(
            user_id=tg_user.id,
            name=tg_user.full_name,
            timezone=TIMEZONE,
            is_admin=_is_admin(tg_user.id),
            ai_access=_is_admin(tg_user.id),
        )
        save_user(record)
        greeting = (
            f"Привет, {tg_user.full_name}! 👋\n"
            "Я FinanceBot v2. Пользователь зарегистрирован."
        )
    else:
        greeting = f"С возвращением, {tg_user.full_name}! 👋"

    await message.answer(greeting, reply_markup=build_main_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Show available commands."""
    await message.answer(
        "Доступные команды:\n"
        "/start — регистрация/перезапуск\n"
        "/help — помощь",
        reply_markup=build_main_keyboard(),
    )
