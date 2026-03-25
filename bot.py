# bot.py
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from telegram import Update
from config import BOT_TOKEN
from handlers import *
from states import UserState

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Botni ishga tushirish"""
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler yaratish (barcha holatlar bilan)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Text("📝 Ro'yxatdan o'tish"), handle_message)
        ],
        states={
            UserState.WAITING_FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_name)
            ],
            UserState.WAITING_LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_last_name)
            ],
            UserState.WAITING_PHONE: [
                MessageHandler(filters.CONTACT, handle_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)
            ],
            UserState.WAITING_PROFESSION: [  # Yangi holat qo'shildi
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profession)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.COMMAND, cancel)
        ],
        name="registration_conversation",
        persistent=False
    )
    
    # Handlerlarni qo'shish
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Botni ishga tushirish
    print("✅ Bot ishga tushdi! (Kasb qo'shilgan versiya)")
    print("📝 Ro'yxatdan o'tish jarayoni: Ism -> Familiya -> Telefon -> Kasb")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()