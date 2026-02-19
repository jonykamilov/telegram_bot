# keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_contact_keyboard():
    """Telefon raqam ulashish tugmasi"""
    keyboard = [[KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_main_menu_keyboard(is_admin=False):
    """Asosiy menyu"""
    keyboard = [
        ["📝 Ro'yxatdan o'tish"],
        ["ℹ️ Ma'lumotlarim"],
        ["🔗 Guruhga obuna"]
    ]
    
    # Admin uchun qo'shimcha tugmalar
    if is_admin:
        keyboard.append(["👥 Foydalanuvchilar", "📊 Statistika"])
        keyboard.append(["📤 Eksport", "📋 Kasblar"])
        keyboard.append(["⚙️ Sozlamalar"])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_users_keyboard():
    """Foydalanuvchilar ro'yxati uchun inline tugmalar"""
    keyboard = [
        [InlineKeyboardButton("📋 Barcha foydalanuvchilar", callback_data="admin_all_users")],
        [InlineKeyboardButton("✅ Obuna bo'lganlar", callback_data="admin_subscribed")],
        [InlineKeyboardButton("❌ Obuna bo'lmaganlar", callback_data="admin_not_subscribed")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📋 Kasb statistikasi", callback_data="admin_profession_stats")],
        [InlineKeyboardButton("📥 Eksport CSV", callback_data="admin_export_csv")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subscription_keyboard(group_link):
    """Obuna bo'lish uchun inline tugmalar"""
    keyboard = [
        [InlineKeyboardButton("🔗 Guruhga obuna bo'lish", url=group_link)],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)