"""
فيكتور - قاعدة البيانات
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import threading

# ═══════════════════════════════════════════════════════════
# 🔧 إعدادات قاعدة البيانات
# ═══════════════════════════════════════════════════════════

DB_NAME = 'victor_database.db'
LOCK = threading.Lock()

# ═══════════════════════════════════════════════════════════
# 🏛️ كلاس قاعدة البيانات الرئيسي
# ═══════════════════════════════════════════════════════════

class Database:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال جديد بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ═══════════════════════════════════════════════════
            # 1. جدول المستخدمين (Users)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned BOOLEAN DEFAULT 0,
                    is_muted BOOLEAN DEFAULT 0,
                    mute_until TIMESTAMP,
                    warnings INTEGER DEFAULT 0,
                    is_premium BOOLEAN DEFAULT 0,
                    language TEXT DEFAULT 'ar',
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 2. جدول الجروبات (Groups)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    group_name TEXT,
                    group_username TEXT,
                    owner_id INTEGER,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    member_count INTEGER DEFAULT 0,
                    welcome_enabled BOOLEAN DEFAULT 1,
                    welcome_text TEXT,
                    welcome_media TEXT,
                    rules_text TEXT,
                    is_protected BOOLEAN DEFAULT 1,
                    silent_mode_start TEXT,
                    silent_mode_end TEXT,
                    bot_nickname TEXT DEFAULT 'فيكتور',
                    settings TEXT DEFAULT '{}'
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 3. جدول العضويات (Memberships)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memberships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    role TEXT DEFAULT 'member',
                    is_active BOOLEAN DEFAULT 1,
                    messages_count INTEGER DEFAULT 0,
                    last_message TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (group_id) REFERENCES groups(group_id),
                    UNIQUE(user_id, group_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 4. جدول الاقتصاد (Economy)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 5000,
                    bank_id TEXT DEFAULT 'victor',
                    bank_balance INTEGER DEFAULT 0,
                    job_id INTEGER,
                    job_start_date TIMESTAMP,
                    daily_income INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    tax_paid INTEGER DEFAULT 0,
                    last_salary TIMESTAMP,
                    tier TEXT DEFAULT 'bronze',
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 5. جدول الممتلكات (Properties)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_id TEXT,
                    item_type TEXT,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    purchase_price INTEGER,
                    current_value INTEGER,
                    daily_income INTEGER DEFAULT 0,
                    is_insured BOOLEAN DEFAULT 0,
                    insurance_type TEXT,
                    last_tax_paid TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 6. جدول المعاملات (Transactions)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user INTEGER,
                    to_user INTEGER,
                    amount INTEGER,
                    type TEXT,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    group_id INTEGER,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 7. جدول الزواج (Marriages)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS marriages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    marriage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dowry_amount INTEGER,
                    dowry_level TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    divorce_date TIMESTAMP,
                    divorce_reason TEXT,
                    shared_balance INTEGER DEFAULT 0,
                    FOREIGN KEY (user1_id) REFERENCES users(user_id),
                    FOREIGN KEY (user2_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 8. جدول العقوبات (Punishments)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS punishments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    type TEXT,
                    reason TEXT,
                    admin_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration INTEGER,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    revoked_by INTEGER,
                    revoked_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (group_id) REFERENCES groups(group_id),
                    FOREIGN KEY (admin_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 9. جدول الكنوز (Treasures)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS treasures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    treasure_type TEXT,
                    amount INTEGER,
                    found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    found_date_only DATE DEFAULT CURRENT_DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 10. جدول المهام (Missions)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS missions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    mission_type TEXT,
                    mission_data TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    reward INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 11. جدول التوبات (Leaderboards)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category TEXT,
                    rank INTEGER,
                    value INTEGER,
                    week_number INTEGER,
                    year INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 12. جدول السجلات (Logs)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_type TEXT,
                    user_id INTEGER,
                    group_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 13. جدول الإعدادات العامة (Global Settings)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by INTEGER
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 14. جدول الضرائب (Taxes)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tax_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    tax_type TEXT,
                    amount INTEGER,
                    income_bracket TEXT,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid BOOLEAN DEFAULT 0,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ═══════════════════════════════════════════════════
            # 15. جدول الوظائف (Jobs History)
            # ═══════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    job_id INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    salary_at_start INTEGER,
                    reason_for_leave TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ قاعدة البيانات جاهزة!")
    
    # ═══════════════════════════════════════════════════════
    # 👤 دوال المستخدمين (Users)
    # ═══════════════════════════════════════════════════════
    
    def add_user(self, user_id: int, username: str = None, full_name: str = None):
        """إضافة مستخدم جديد"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, full_name))
            
            # إنشاء حساب اقتصادي تلقائياً
            cursor.execute('''
                INSERT OR IGNORE INTO economy (user_id, balance)
                VALUES (?, 5000)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """جلب بيانات مستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs):
        """تحديث بيانات مستخدم"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            
            cursor.execute(f'''
                UPDATE users SET {fields}, last_seen = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', values)
            
            conn.commit()
            conn.close()
    
    def ban_user(self, user_id: int, group_id: int = None, 
                 admin_id: int = None, reason: str = None, 
                 duration: int = None):
        """حظر مستخدم"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            expires_at = None
            if duration:
                expires_at = datetime.now() + timedelta(minutes=duration)
            
            cursor.execute('''
                INSERT INTO punishments 
                (user_id, group_id, type, reason, admin_id, duration, expires_at)
                VALUES (?, ?, 'ban', ?, ?, ?, ?)
            ''', (user_id, group_id, reason, admin_id, duration, expires_at))
            
            if not group_id:  # بان عام
                cursor.execute('''
                    UPDATE users SET is_banned = 1 WHERE user_id = ?
                ''', (user_id,))
            
            conn.commit()
            conn.close()
    
    def mute_user(self, user_id: int, group_id: int = None,
                  admin_id: int = None, duration: int = 60):
        """كتم مستخدم"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            mute_until = datetime.now() + timedelta(minutes=duration)
            
            cursor.execute('''
                INSERT INTO punishments 
                (user_id, group_id, type, admin_id, duration, expires_at)
                VALUES (?, ?, 'mute', ?, ?, ?)
            ''', (user_id, group_id, admin_id, duration, mute_until))
            
            cursor.execute('''
                UPDATE users SET is_muted = 1, mute_until = ? WHERE user_id = ?
            ''', (mute_until, user_id))
            
            conn.commit()
            conn.close()
    
    def warn_user(self, user_id: int, group_id: int = None,
                  admin_id: int = None, reason: str = None):
        """تحذير مستخدم"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO punishments 
                (user_id, group_id, type, reason, admin_id)
                VALUES (?, ?, 'warn', ?, ?)
            ''', (user_id, group_id, reason, admin_id))
            
            cursor.execute('''
                UPDATE users SET warnings = warnings + 1 WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # التحقق من عدد التحذيرات
            user = self.get_user(user_id)
            if user and user['warnings'] >= 3:
                self.ban_user(user_id, group_id, admin_id, "3 تحذيرات")
                return True  # تم الحظر
            return False
    
    # ═══════════════════════════════════════════════════════
    # 👥 دوال الجروبات (Groups)
    # ═══════════════════════════════════════════════════════
    
    def add_group(self, group_id: int, group_name: str, 
                  owner_id: int, group_username: str = None):
        """إضافة جروب جديد"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO groups 
                (group_id, group_name, group_username, owner_id)
                VALUES (?, ?, ?, ?)
            ''', (group_id, group_name, group_username, owner_id))
            
            conn.commit()
            conn.close()
    
    def get_group(self, group_id: int) -> Optional[Dict]:
        """جلب بيانات جروب"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def update_group(self, group_id: int, **kwargs):
        """تحديث إعدادات جروب"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [group_id]
            
            cursor.execute(f'''
                UPDATE groups SET {fields} WHERE group_id = ?
            ''', values)
            
            conn.commit()
            conn.close()
    
    # ═══════════════════════════════════════════════════════
    # 💰 دوال الاقتصاد (Economy)
    # ═══════════════════════════════════════════════════════
    
    def get_balance(self, user_id: int) -> Dict:
        """جلب رصيد مستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM economy WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            # إنشاء حساب جديد
            cursor.execute('''
                INSERT INTO economy (user_id, balance) VALUES (?, 5000)
            ''', (user_id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM economy WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        
        conn.close()
        return dict(row)
    
    def update_balance(self, user_id: int, amount: int, 
                       transaction_type: str = 'transfer',
                       description: str = None,
                       group_id: int = None):
        """تحديث رصيد مستخدم"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # جلب الرصيد الحالي
            current = self.get_balance(user_id)
            new_balance = current['balance'] + amount
            
            if new_balance < 0:
                conn.close()
                return False  # رصيد غير كافي
            
            # تحديث الرصيد
            cursor.execute('''
                UPDATE economy SET balance = ? WHERE user_id = ?
            ''', (new_balance, user_id))
            
            # تسجيل المعاملة
            from_user = user_id if amount < 0 else None
            to_user = user_id if amount > 0 else None
            
            cursor.execute('''
                INSERT INTO transactions 
                (from_user, to_user, amount, type, description, group_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (from_user, to_user, abs(amount), transaction_type, 
                  description, group_id))
            
            conn.commit()
            conn.close()
            return True
    
    def transfer_money(self, from_user: int, to_user: int, 
                       amount: int, description: str = None) -> bool:
        """تحويل فلوس بين مستخدمين"""
        with LOCK:
            # التحقق من الرصيد
            sender = self.get_balance(from_user)
            if sender['balance'] < amount:
                return False
            
            # خصم من المرسل
            if not self.update_balance(from_user, -amount, 'transfer', description):
                return False
            
            # إضافة للمستلم
            self.update_balance(to_user, amount, 'transfer', description)
            
            return True
    
    def change_bank(self, user_id: int, new_bank_id: str) -> bool:
        """تغيير بنك المستخدم"""
        from config import BANKS
        
        if new_bank_id not in BANKS:
            return False
        
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE economy SET bank_id = ? WHERE user_id = ?
            ''', (new_bank_id, user_id))
            
            conn.commit()
            conn.close()
            return True
    
    def set_job(self, user_id: int, job_id: int):
        """تعيين وظيفة"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # إنهاء الوظيفة السابقة
            cursor.execute('''
                UPDATE job_history SET ended_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND ended_at IS NULL
            ''', (user_id,))
            
            # تعيين الجديدة
            cursor.execute('''
                UPDATE economy SET job_id = ?, job_start_date = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (job_id, user_id))
            
            cursor.execute('''
                INSERT INTO job_history (user_id, job_id, salary_at_start)
                SELECT ?, ?, daily_income FROM economy WHERE user_id = ?
            ''', (user_id, job_id, user_id))
            
            conn.commit()
            conn.close()
    
    def collect_salary(self, user_id: int) -> int:
        """صرف راتب"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # التحقق من آخر راتب
            cursor.execute('''
                SELECT last_salary, daily_income FROM economy WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return 0
            
            last_salary = row['last_salary']
            daily_income = row['daily_income']
            
            # التحقق من مرور 24 ساعة
            if last_salary:
                last = datetime.fromisoformat(last_salary)
                if datetime.now() - last < timedelta(hours=20):
                    conn.close()
                    return -1  # لسه بدري
            
            # صرف الراتب
            cursor.execute('''
                UPDATE economy 
                SET balance = balance + ?, last_salary = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (daily_income, user_id))
            
            conn.commit()
            conn.close()
            return daily_income
    
    # ═══════════════════════════════════════════════════════
    # 🛒 دوال المتجر والممتلكات (Shop & Properties)
    # ═══════════════════════════════════════════════════════
    
    def buy_item(self, user_id: int, item_id: str, 
                 item_type: str, price: int,
                 daily_income: int = 0) -> bool:
        """شراء سلعة"""
        # التحقق من الرصيد
        if not self.update_balance(user_id, -price, 'purchase', f'شراء {item_id}'):
            return False
        
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO properties 
                (user_id, item_id, item_type, purchase_price, current_value, daily_income)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, item_id, item_type, price, price, daily_income))
            
            # تحديث الدخل اليومي إذا كان عقار
            if daily_income > 0:
                cursor.execute('''
                    UPDATE economy SET daily_income = daily_income + ?
                    WHERE user_id = ?
                ''', (daily_income, user_id))
            
            conn.commit()
            conn.close()
            return True
    
    def get_properties(self, user_id: int) -> List[Dict]:
        """جلب ممتلكات مستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM properties WHERE user_id = ?
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ═══════════════════════════════════════════════════════
    # 💍 دوال الزواج (Marriage)
    # ═══════════════════════════════════════════════════════
    
    def marry(self, user1_id: int, user2_id: int, 
              dowry: int, level: str) -> bool:
        """تسجيل زواج"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # التحقق من عدم وجود زواج سابق
            cursor.execute('''
                SELECT * FROM marriages 
                WHERE (user1_id = ? OR user2_id = ? OR user1_id = ? OR user2_id = ?)
                AND is_active = 1
            ''', (user1_id, user1_id, user2_id, user2_id))
            
            if cursor.fetchone():
                conn.close()
                return False  # واحد منهم متزوج
            
            cursor.execute('''
                INSERT INTO marriages 
                (user1_id, user2_id, dowry_amount, dowry_level, shared_balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (user1_id, user2_id, dowry, level, dowry // 2))
            
            conn.commit()
            conn.close()
            return True
    
    def get_marriage(self, user_id: int) -> Optional[Dict]:
        """جلب بيانات زواج"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM marriages 
            WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1
        ''', (user_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def divorce(self, marriage_id: int, reason: str = None):
        """طلاق"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE marriages 
                SET is_active = 0, divorce_date = CURRENT_TIMESTAMP, divorce_reason = ?
                WHERE id = ?
            ''', (reason, marriage_id))
            
            conn.commit()
            conn.close()
    
    # ═══════════════════════════════════════════════════════
    # 🎁 دوال الكنوز (Treasures)
    # ═══════════════════════════════════════════════════════
    
    def can_find_treasure(self, user_id: int) -> bool:
        """التحقق من إمكانية البحث عن كنز"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM treasures 
            WHERE user_id = ? AND found_date_only = DATE('now')
        ''', (user_id,))
        
        count = cursor.fetchone()['count']
        conn.close()
        return count < 2  # مرتين يومياً
    
    def add_treasure(self, user_id: int, treasure_type: str, amount: int):
        """إضافة كنز"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO treasures (user_id, treasure_type, amount)
                VALUES (?, ?, ?)
            ''', (user_id, treasure_type, amount))
            
            conn.commit()
            conn.close()
            
            # إضافة للرصيد
            self.update_balance(user_id, amount, 'treasure', 'كنز')
    
    # ═══════════════════════════════════════════════════════
    # 📊 دوال الإحصائيات (Statistics)
    # ═══════════════════════════════════════════════════════
    
    def get_leaderboard(self, category: str = 'balance', 
                        limit: int = 10) -> List[Dict]:
        """جلب توب"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category == 'balance':
            cursor.execute('''
                SELECT u.user_id, u.username, u.full_name, e.balance
                FROM users u
                JOIN economy e ON u.user_id = e.user_id
                ORDER BY e.balance DESC
                LIMIT ?
            ''', (limit,))
        
        elif category == 'richest':
            cursor.execute('''
                SELECT u.user_id, u.username, u.full_name,
                       (e.balance + e.bank_balance + COALESCE(
                           (SELECT SUM(current_value) FROM properties WHERE user_id = u.user_id), 0
                       )) as total_wealth
                FROM users u
                JOIN economy e ON u.user_id = e.user_id
                ORDER BY total_wealth DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_group_stats(self, group_id: int) -> Dict:
        """إحصائيات جروب"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as members,
                   SUM(CASE WHEN last_seen > datetime('now', '-1 day') THEN 1 ELSE 0 END) as active_today
            FROM memberships
            WHERE group_id = ? AND is_active = 1
        ''', (group_id,))
        
        stats = dict(cursor.fetchone())
        conn.close()
        return stats
    
    # ═══════════════════════════════════════════════════════
    # 📝 دوال السجلات (Logs)
    # ═══════════════════════════════════════════════════════
    
    def add_log(self, log_type: str, action: str, 
                user_id: int = None, group_id: int = None,
                details: str = None):
        """إضافة سجل"""
        with LOCK:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs (log_type, user_id, group_id, action, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (log_type, user_id, group_id, action, details))
            
            conn.commit()
            conn.close()
    
    def get_logs(self, log_type: str = None, user_id: int = None,
                 limit: int = 100) -> List[Dict]:
        """جلب سجلات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        
        if log_type:
            query += ' AND log_type = ?'
            params.append(log_type)
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# ═══════════════════════════════════════════════════════════
# 🚀 إنشاء instance عالمي
# ═══════════════════════════════════════════════════════════

db = Database()

# ═══════════════════════════════════════════════════════════
# ✅ نهاية الملف
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("✅ قاعدة البيانات جاهزة للعمل!")
    print(f"📊 عدد الجداول: 15")
