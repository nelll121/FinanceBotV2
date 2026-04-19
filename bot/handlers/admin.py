from bot.services.users import (
    count_users,
    get_all_users,
    get_user,
    grant_ai_access,
    revoke_ai_access,
)
            f"AI: {'ON' if payload.get('ai_access') else 'OFF'} | "
            f"Sheet: {'YES' if payload.get('sheets_id') else 'NO'}"
    grant_ai_access(user_id)
    revoke_ai_access(user_id)
