# handlers.py (faqat o'zgartirilgan qismlar)
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import GROUP_LINK, CHANNEL_ID, ADMIN_IDS
from database import Database
from keyboards import (
    get_contact_keyboard, get_main_menu_keyboard, 
    get_subscription_keyboard, get_admin_users_keyboard
)
from states import UserState, set_state

# Database obyektini yaratish
db = Database()

# Admin funksiyalari
def is_admin(user_id):
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user_id = update.effective_user.id
    
    # Foydalanuvchini tekshirish
    if db.user_exists(user_id):
        await update.message.reply_text(
            "👋 Xush kelibsiz! Siz allaqachon ro'yxatdan o'tgansiz.",
            reply_markup=get_main_menu_keyboard(is_admin(user_id))
        )
    else:
        await update.message.reply_text(
            "👋 Assalomu alaykum! Botimizga xush kelibsiz.\n\n"
            "Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n"
            "Iltimos, ismingizni kiriting:"
        )
        await set_state(context, user_id, UserState.WAITING_FIRST_NAME)
        return UserState.WAITING_FIRST_NAME

async def handle_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ismni qabul qilish"""
    user_id = update.effective_user.id
    first_name = update.message.text
    
    # Ismni vaqtincha saqlash
    context.user_data['temp_first_name'] = first_name
    
    await update.message.reply_text(
        f"Rahmat, {first_name}!\nEndi familiyangizni kiriting:"
    )
    await set_state(context, user_id, UserState.WAITING_LAST_NAME)
    return UserState.WAITING_LAST_NAME

async def handle_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Familiyani qabul qilish"""
    user_id = update.effective_user.id
    last_name = update.message.text
    
    # Familiyani vaqtincha saqlash
    context.user_data['temp_last_name'] = last_name
    
    await update.message.reply_text(
        "Endi telefon raqamingizni ulashing.\n"
        "Pastdagi tugma orqali raqamingizni yuboring:",
        reply_markup=get_contact_keyboard()
    )
    await set_state(context, user_id, UserState.WAITING_PHONE)
    return UserState.WAITING_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamni qabul qilish"""
    user_id = update.effective_user.id
    
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
    
    # Telefon raqamni vaqtincha saqlash
    context.user_data['temp_phone'] = phone_number
    
    await update.message.reply_text(
        "✅ Telefon raqam qabul qilindi!\n\n"
        "Endi kasbingizni yozib yuboring (masalan: Dasturchi, O'qituvchi, Shifokor va h.k.):",
        reply_markup=None  # Tugmalarni olib tashlaymiz
    )
    await set_state(context, user_id, UserState.WAITING_PROFESSION)
    return UserState.WAITING_PROFESSION

async def handle_profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kasbni qabul qilish va ro'yxatdan o'tkazish"""
    user_id = update.effective_user.id
    profession = update.message.text.strip()
    
    # Vaqtincha saqlangan ma'lumotlarni olish
    first_name = context.user_data.get('temp_first_name', '')
    last_name = context.user_data.get('temp_last_name', '')
    phone_number = context.user_data.get('temp_phone', '')
    
    # Foydalanuvchini bazaga qo'shish (kasb bilan) - 5 argument
    if db.add_user(user_id, first_name, last_name, phone_number, profession):
        await update.message.reply_text(
            f"✅ Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            f"👤 Ism: {first_name}\n"
            f"👤 Familiya: {last_name}\n"
            f"📞 Telefon: {phone_number}\n"
            f"💼 Kasb: {profession}\n\n"
            f"Endi guruhimizga obuna bo'lishingiz kerak.",
            reply_markup=get_main_menu_keyboard(is_admin(user_id))
        )
        
        # Obuna bo'lish uchun xabar yuborish
        await update.message.reply_text(
            "🔔 Iltimos, quyidagi guruhga obuna bo'ling:",
            reply_markup=get_subscription_keyboard(GROUP_LINK)
        )
    else:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
        )
    
    # Vaqtincha ma'lumotlarni tozalash
    context.user_data.clear()
    await set_state(context, user_id, UserState.IDLE)
    return ConversationHandler.END

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ma'lumotlarini ko'rsatish (kasb bilan)"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if user:
        subscription_status = "✅ Ha" if user[7] else "❌ Yo'q"
        info_text = f"""
📋 Sizning ma'lumotlaringiz:

👤 Ism: {user[2]}
👤 Familiya: {user[3]}
📞 Telefon: {user[4]}
💼 Kasb: {user[5]}
📅 Ro'yxatdan o'tgan: {user[6]}
🔔 Obuna: {subscription_status}
        """
        await update.message.reply_text(info_text.strip())
    else:
        await update.message.reply_text(
            "Siz hali ro'yxatdan o'tmagansiz. Ro'yxatdan o'tish uchun /start ni bosing."
        )

async def show_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obuna bo'lish linkini ko'rsatish"""
    await update.message.reply_text(
        "🔔 Guruhga obuna bo'lish uchun quyidagi linkni bosing:",
        reply_markup=get_subscription_keyboard(GROUP_LINK)
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obunani tekshirish"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    try:
        # Foydalanuvchi guruh a'zosi ekanligini tekshirish
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        if chat_member.status in ['member', 'administrator', 'creator']:
            db.update_subscription(user_id, True)
            await query.edit_message_text(
                "✅ Obunangiz tasdiqlandi! Botdan to'liq foydalanishingiz mumkin."
            )
        else:
            await query.edit_message_text(
                "❌ Siz hali guruhga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling.",
                reply_markup=get_subscription_keyboard(GROUP_LINK)
            )
    except Exception as e:
        await query.edit_message_text(
            "❌ Obunani tekshirishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=get_subscription_keyboard(GROUP_LINK)
        )

# Admin panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panelni ko'rsatish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    await update.message.reply_text(
        "👨‍💼 Admin panel\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=get_admin_users_keyboard()
    )

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin callbacklarini qayta ishlash"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text("❌ Siz admin emassiz!")
        return
    
    data = query.data
    
    if data == "admin_all_users":
        users = db.get_all_users()
        if users:
            text = "📋 Barcha foydalanuvchilar (oxirgi 10 ta):\n\n"
            for user in users[:10]:
                if len(user) >= 8:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n💼 {user[5]}\n📅 {user[6]}\n🔔 {'✅' if user[7] else '❌'}\n---\n"
                else:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n📅 {user[5]}\n🔔 {'✅' if user[6] else '❌'}\n💼 Kiritilmagan\n---\n"
            text += f"\nJami: {len(users)} ta foydalanuvchi"
            await query.edit_message_text(text, reply_markup=get_admin_users_keyboard())
        else:
            await query.edit_message_text("📭 Hali foydalanuvchilar yo'q", reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_subscribed":
        users = db.get_subscribed_users()
        if users:
            text = "✅ Obuna bo'lgan foydalanuvchilar (oxirgi 10 ta):\n\n"
            for user in users[:10]:
                if len(user) >= 8:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n💼 {user[5]}\n📅 {user[6]}\n---\n"
                else:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n📅 {user[5]}\n💼 Kiritilmagan\n---\n"
            text += f"\nJami: {len(users)} ta"
            await query.edit_message_text(text, reply_markup=get_admin_users_keyboard())
        else:
            await query.edit_message_text("📭 Obuna bo'lgan foydalanuvchilar yo'q", reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_not_subscribed":
        users = db.get_unsubscribed_users()
        if users:
            text = "❌ Obuna bo'lmagan foydalanuvchilar (oxirgi 10 ta):\n\n"
            for user in users[:10]:
                if len(user) >= 8:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n💼 {user[5]}\n📅 {user[6]}\n---\n"
                else:
                    text += f"👤 {user[2]} {user[3]}\n📞 {user[4]}\n📅 {user[5]}\n💼 Kiritilmagan\n---\n"
            text += f"\nJami: {len(users)} ta"
            await query.edit_message_text(text, reply_markup=get_admin_users_keyboard())
        else:
            await query.edit_message_text("✅ Barcha foydalanuvchilar obuna bo'lgan", reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_stats":
        stats = db.get_statistics()
        total = stats['total']
        text = f"""
📊 UMUMIY STATISTIKA

👥 Jami foydalanuvchilar: {stats['total']}
✅ Obuna bo'lganlar: {stats['subscribed']}
❌ Obuna bo'lmaganlar: {stats['unsubscribed']}
📅 Bugun ro'yxatdan o'tganlar: {stats['today_registered']}

📈 Foizlar:
✅ Obuna: {stats['subscribed']/total*100 if total > 0 else 0:.1f}%
❌ Obuna emas: {stats['unsubscribed']/total*100 if total > 0 else 0:.1f}%
        """
        await query.edit_message_text(text, reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_profession_stats":
        try:
            professions = db.get_profession_statistics()
            if professions:
                text = "📋 KASBLAR STATISTIKASI\n\n"
                total_users = db.get_statistics()['total']
                for prof, count in professions[:15]:
                    percentage = (count / total_users * 100) if total_users > 0 else 0
                    text += f"💼 {prof}: {count} ta ({percentage:.1f}%)\n"
                await query.edit_message_text(text, reply_markup=get_admin_users_keyboard())
            else:
                await query.edit_message_text("📭 Kasb ma'lumotlari yo'q", reply_markup=get_admin_users_keyboard())
        except Exception as e:
            await query.edit_message_text("❌ Kasb statistikasini olishda xatolik", reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_export_csv":
        try:
            csv_data = db.export_to_csv()
            await query.message.reply_document(
                document=csv_data.encode('utf-8'),
                filename='foydalanuvchilar.csv',
                caption="📥 Foydalanuvchilar ro'yxati"
            )
            # Xabarni o'zgartirmaymiz, faqat dokument yuboramiz
            await query.edit_message_text("✅ CSV fayl yuborildi!", reply_markup=get_admin_users_keyboard())
        except Exception as e:
            print(f"CSV export xatosi: {e}")
            await query.edit_message_text("❌ CSV eksport qilishda xatolik", reply_markup=get_admin_users_keyboard())
    
    elif data == "admin_back":
        await query.edit_message_text(
            "👨‍💼 Admin panel\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=get_admin_users_keyboard()
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Amalni bekor qilish"""
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Amal bekor qilindi.",
        reply_markup=get_main_menu_keyboard(is_admin(user_id))
    )
    context.user_data.clear()
    await set_state(context, user_id, UserState.IDLE)
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oddiy xabarlarni qayta ishlash"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "📝 Ro'yxatdan o'tish":
        if db.user_exists(user_id):
            await update.message.reply_text("Siz allaqachon ro'yxatdan o'tgansiz!")
        else:
            await update.message.reply_text("Ismingizni kiriting:")
            await set_state(context, user_id, UserState.WAITING_FIRST_NAME)
            return UserState.WAITING_FIRST_NAME
    
    elif text == "ℹ️ Ma'lumotlarim":
        await show_info(update, context)
    
    elif text == "🔗 Guruhga obuna":
        await show_subscription(update, context)
    
    # Admin tugmalari
    elif text == "👥 Foydalanuvchilar" and is_admin(user_id):
        await admin_panel(update, context)
    
    elif text == "📊 Statistika" and is_admin(user_id):
        stats = db.get_statistics()
        stat_text = f"""
📊 STATISTIKA

👥 Jami foydalanuvchilar: {stats['total']}
✅ Obuna bo'lganlar: {stats['subscribed']}
❌ Obuna bo'lmaganlar: {stats['unsubscribed']}
📅 Bugun ro'yxatdan o'tganlar: {stats['today_registered']}
        """
        await update.message.reply_text(stat_text)
    
    elif text == "📋 Kasblar" and is_admin(user_id):
        professions = db.get_profession_statistics()
        if professions:
            prof_text = "📋 KASBLAR STATISTIKASI\n\n"
            for prof, count in professions[:15]:
                prof_text += f"💼 {prof}: {count} ta\n"
            await update.message.reply_text(prof_text)
        else:
            await update.message.reply_text("📭 Ma'lumot yo'q")
    
    elif text == "📤 Eksport" and is_admin(user_id):
        csv_data = db.export_to_csv()
        await update.message.reply_document(
            document=csv_data.encode('utf-8'),
            filename='foydalanuvchilar.csv',
            caption="📥 Foydalanuvchilar ro'yxati (kasb bilan)"
        )