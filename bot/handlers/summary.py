"""Summary handlers."""

from __future__ import annotations
from bot.keyboards import build_main_keyboard
from bot.services.sheets import SheetsService
from bot.services.users import get_user

    if message.from_user is None:
        return

    user = get_user(message.from_user.id)
    if user is None or not user.get("sheets_id"):
        await message.answer("Сначала завершите /start и подключите таблицу.", reply_markup=build_main_keyboard())
        return

    service = SheetsService(str(user["sheets_id"]))
    summary = service.get_month_summary()

    await message.answer(
        "📊 Сводка месяца\n"
        f"Месяц: {summary['month']}\n"
        f"Доход: {summary['income']:.2f}\n"
        f"Расход: {summary['expense']:.2f}\n"
        f"Баланс: {summary['balance']:.2f}",
        reply_markup=build_main_keyboard(),
    )
