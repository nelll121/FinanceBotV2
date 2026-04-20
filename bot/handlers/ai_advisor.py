"""AI advisor chat handlers."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque
from bot.keyboards import build_main_keyboard
from bot.services.ai_service import get_ai_response
from bot.services.sheets import SheetsService
from bot.services.users import get_user

CHAT_HISTORY: dict[int, Deque[dict[str, str]]] = defaultdict(lambda: deque(maxlen=10))
AI_MODE_USERS: set[int] = set()

    if message.from_user is None:
        return

    user = get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала завершите /start и подключите таблицу.")
        return

    if not user.get("ai_access") and not user.get("api_key"):
        await message.answer(
            "ИИ пока недоступен для вас. Попросите администратора выдать доступ через /grant.",
            reply_markup=build_main_keyboard(),
        )
        return

    AI_MODE_USERS.add(message.from_user.id)
    await message.answer(
        "Режим ИИ-советника включён. Напишите вопрос по вашим финансам.\n"
        "Чтобы выйти: отправьте 'выход' или нажмите кнопку другого раздела.",
    )


@router.message(F.text.lower() == "выход")
async def ai_exit(message: Message) -> None:
    if message.from_user is None:
        return

    if message.from_user.id in AI_MODE_USERS:
        AI_MODE_USERS.discard(message.from_user.id)
        await message.answer("Режим ИИ-советника выключен.", reply_markup=build_main_keyboard())


@router.message()
async def ai_chat_handler(message: Message) -> None:
    if message.from_user is None:
        return

    user_id = message.from_user.id
    if user_id not in AI_MODE_USERS:
        return

    user = get_user(user_id)
    if user is None or not user.get("sheets_id"):
        await message.answer("Не найдена привязанная таблица. Выполните /start.")
        return

    service = SheetsService(str(user["sheets_id"]))
    context = {
        "month_summary": service.get_month_summary(),
        "active_debts": service.get_active_debts(),
        "savings_goals": service.get_savings_goals(),
    }

    history = list(CHAT_HISTORY[user_id])
    response = await get_ai_response(
        user_id=user_id,
        context=context,
        history=history,
        message=message.text or "",
    )

    CHAT_HISTORY[user_id].append({"role": "user", "content": message.text or ""})
    CHAT_HISTORY[user_id].append({"role": "assistant", "content": response})
    await message.answer(response)
