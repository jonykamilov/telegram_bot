# states.py
from telegram.ext import ContextTypes

class UserState:
    """Foydalanuvchi holatlari"""
    IDLE = 0
    WAITING_FIRST_NAME = 1
    WAITING_LAST_NAME = 2
    WAITING_PHONE = 3
    WAITING_PROFESSION = 4  # Yangi holat - bu qator qo'shilganligiga ishonch hosil qiling

# Har bir foydalanuvchi holatini saqlash uchun
async def get_state(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> int:
    """Foydalanuvchi holatini olish"""
    return context.user_data.get('state', UserState.IDLE)

async def set_state(context: ContextTypes.DEFAULT_TYPE, user_id: int, state: int):
    """Foydalanuvchi holatini o'rnatish"""
    context.user_data['state'] = state