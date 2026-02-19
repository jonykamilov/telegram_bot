# database.py
import sqlite3
from datetime import datetime
import csv
from io import StringIO

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()
    
    def create_table(self):
        """Foydalanuvchilar jadvalini yaratish (kasb ustuni bilan)"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                profession TEXT,
                registered_date TEXT,
                is_subscribed BOOLEAN DEFAULT 0
            )
        ''')
        self.connection.commit()
    
    def add_user(self, user_id, first_name, last_name, phone_number, profession):
        """Yangi foydalanuvchi qo'shish (kasb bilan)"""
        try:
            self.cursor.execute('''
                INSERT INTO users (user_id, first_name, last_name, phone_number, profession, registered_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, first_name, last_name, phone_number, profession, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Foydalanuvchi allaqachon ro'yxatdan o'tgan
    
    def get_user(self, user_id):
        """Foydalanuvchi ma'lumotlarini olish"""
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def update_subscription(self, user_id, is_subscribed):
        """Obuna holatini yangilash"""
        self.cursor.execute('UPDATE users SET is_subscribed = ? WHERE user_id = ?', (is_subscribed, user_id))
        self.connection.commit()
    
    def user_exists(self, user_id):
        """Foydalanuvchi mavjudligini tekshirish"""
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone() is not None
    
    # Admin funksiyalari
    def get_all_users(self):
        """Barcha foydalanuvchilarni olish"""
        self.cursor.execute('SELECT * FROM users ORDER BY registered_date DESC')
        return self.cursor.fetchall()
    
    def get_subscribed_users(self):
        """Obuna bo'lgan foydalanuvchilarni olish"""
        self.cursor.execute('SELECT * FROM users WHERE is_subscribed = 1 ORDER BY registered_date DESC')
        return self.cursor.fetchall()
    
    def get_unsubscribed_users(self):
        """Obuna bo'lmagan foydalanuvchilarni olish"""
        self.cursor.execute('SELECT * FROM users WHERE is_subscribed = 0 ORDER BY registered_date DESC')
        return self.cursor.fetchall()
    
    def get_users_by_profession(self, profession):
        """Kasb bo'yicha foydalanuvchilarni olish"""
        self.cursor.execute('SELECT * FROM users WHERE profession LIKE ? ORDER BY registered_date DESC', (f'%{profession}%',))
        return self.cursor.fetchall()
    
    def get_profession_statistics(self):
        """Kasblar bo'yicha statistika"""
        self.cursor.execute('SELECT profession, COUNT(*) FROM users GROUP BY profession ORDER BY COUNT(*) DESC')
        return self.cursor.fetchall()
    
    def get_statistics(self):
        """Statistika ma'lumotlarini olish"""
        self.cursor.execute('SELECT COUNT(*) FROM users')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1')
        subscribed = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 0')
        unsubscribed = self.cursor.fetchone()[0]
        
        # Bugun ro'yxatdan o'tganlar
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE registered_date LIKE ?', (f'{today}%',))
        today_registered = self.cursor.fetchone()[0]
        
        return {
            'total': total,
            'subscribed': subscribed,
            'unsubscribed': unsubscribed,
            'today_registered': today_registered
        }
    
    # MUHIM: export_to_csv funksiyasi
    def export_to_csv(self):
        """Ma'lumotlarni CSV formatida eksport qilish (kasb bilan)"""
        users = self.get_all_users()
        output = StringIO()
        writer = csv.writer(output)
        
        # Sarlavhalar
        writer.writerow(['ID', 'User ID', 'Ism', 'Familiya', 'Telefon', 'Kasb', 'Ro\'yxatdan o\'tgan', 'Obuna'])
        
        # Ma'lumotlar
        for user in users:
            if len(user) >= 8:  # Yangi struktura
                writer.writerow([
                    user[0], user[1], user[2], user[3], user[4], user[5],
                    user[6], 'Ha' if user[7] else 'Yo\'q'
                ])
            else:  # Eski struktura
                writer.writerow([
                    user[0], user[1], user[2], user[3], user[4],
                    "Kiritilmagan",  # Kasb yo'q
                    user[5], 'Ha' if user[6] else 'Yo\'q'
                ])
        
        return output.getvalue()
    
    def close(self):
        """Bazani yopish"""
        self.connection.close()