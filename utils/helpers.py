"""
فيكتور - الدوال المساعدة
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import re
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class Helpers:
    """مكتبة الدوال المساعدة"""
    
    # ═══════════════════════════════════════════════════════
    # 🔤 التحقق والتنظيف
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def clean_text(text: str) -> str:
        """تنظيف النص من المسافات الزائدة والرموز"""
        if not text:
            return ""
        
        # إزالة المسافات الزائدة
        text = " ".join(text.split())
        
        # إزالة الرموز الخطرة
        dangerous = ['<script>', '</script>', 'javascript:', 'onerror=', 'onload=']
        for d in dangerous:
            text = text.replace(d, '')
        
        return text.strip()
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """التحقق من صحة اسم المستخدم"""
        if not username:
            return False
        
        # يجب أن يبدأ بحرف ويحتوي على أحرف وأرقام وشرطات سفلية فقط
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]{3,31}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """التحقق من صحة الإيميل"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def contains_arabic(text: str) -> bool:
        """التحقق إذا كان النص يحتوي على عربي"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
        return bool(arabic_pattern.search(text))
    
    @staticmethod
    def contains_english(text: str) -> bool:
        """التحقق إذا كان النص يحتوي على إنجليزي"""
        return bool(re.search(r'[a-zA-Z]', text))
    
    # ═══════════════════════════════════════════════════════
    # 🔢 التحويلات والتنسيق
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def format_number(number: int, decimal_places: int = 0) -> str:
        """تنسيق الرقم بفواصل"""
        if decimal_places > 0:
            return f"{number:,.{decimal_places}f}"
        return f"{number:,}"
    
    @staticmethod
    def format_currency(amount: int, symbol: str = "🏆") -> str:
        """تنسيق العملة"""
        return f"{Helpers.format_number(amount)} {symbol}"
    
    @staticmethod
    def format_time_ago(timestamp: datetime) -> str:
        """تنسيق الوقت المنقضي"""
        now = datetime.now()
        diff = now - timestamp
        
        seconds = int(diff.total_seconds())
        
        if seconds < 60:
            return "الآن"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"منذ {minutes} دقيقة"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"منذ {hours} ساعة"
        elif seconds < 604800:
            days = seconds // 86400
            return f"منذ {days} يوم"
        elif seconds < 2592000:
            weeks = seconds // 604800
            return f"منذ {weeks} أسبوع"
        else:
            months = seconds // 2592000
            return f"منذ {months} شهر"
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """تنسيق المدة"""
        if minutes < 60:
            return f"{minutes} دقيقة"
        elif minutes < 1440:
            hours = minutes // 60
            remaining = minutes % 60
            if remaining > 0:
                return f"{hours} ساعة و {remaining} دقيقة"
            return f"{hours} ساعة"
        else:
            days = minutes // 1440
            remaining = minutes % 1440
            hours = remaining // 60
            if hours > 0:
                return f"{days} يوم و {hours} ساعة"
            return f"{days} يوم"
    
    @staticmethod
    def bytes_to_human(size_bytes: int) -> str:
        """تحويل البايت لصيغة مقروءة"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    # ═══════════════════════════════════════════════════════
    # 🎲 العشوائية والتوليد
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """توليد نص عشوائي"""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    @staticmethod
    def generate_random_number(min_val: int = 1000, max_val: int = 9999) -> int:
        """توليد رقم عشوائي"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def generate_id() -> str:
        """توليد معرف فريد"""
        timestamp = int(datetime.now().timestamp())
        random_part = Helpers.generate_random_string(6)
        return f"{timestamp}_{random_part}"
    
    @staticmethod
    def shuffle_list(input_list: List) -> List:
        """خلط قائمة"""
        result = input_list.copy()
        random.shuffle(result)
        return result
    
    @staticmethod
    def pick_random(items: List, count: int = 1) -> Any:
        """اختيار عشوائي من قائمة"""
        if count == 1:
            return random.choice(items)
        return random.sample(items, min(count, len(items)))
    
    # ═══════════════════════════════════════════════════════
    # 🔐 الأمان والتشفير
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def hash_simple(text: str) -> str:
        """تشفير بسيط (للتوضيح فقط - استخدم bcrypt في الإنتاج)"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:10]
    
    @staticmethod
    def mask_sensitive(text: str, visible_start: int = 2, visible_end: int = 2) -> str:
        """إخفاء جزء من النص الحساس"""
        if len(text) <= visible_start + visible_end:
            return "*" * len(text)
        
        start = text[:visible_start]
        end = text[-visible_end:]
        middle = "*" * (len(text) - visible_start - visible_end)
        
        return f"{start}{middle}{end}"
    
    @staticmethod
    def is_safe_input(text: str, max_length: int = 1000) -> bool:
        """التحقق من أمان المدخلات"""
        if not text or len(text) > max_length:
            return False
        
        # التحقق من عدم وجود أكواد ضارة
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True
    
    # ═══════════════════════════════════════════════════════
    # 📊 الإحصائيات والتحليل
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_percentage(part: int, total: int) -> float:
        """حساب النسبة المئوية"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
    
    @staticmethod
    def calculate_average(numbers: List[int]) -> float:
        """حساب المتوسط"""
        if not numbers:
            return 0.0
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def find_most_common(items: List) -> Any:
        """إيجاد الأكثر تكراراً"""
        if not items:
            return None
        
        from collections import Counter
        counter = Counter(items)
        return counter.most_common(1)[0][0]
    
    @staticmethod
    def group_by(items: List[Dict], key: str) -> Dict:
        """تجميع قائمة حسب مفتاح"""
        result = {}
        for item in items:
            group_key = item.get(key)
            if group_key not in result:
                result[group_key] = []
            result[group_key].append(item)
        return result
    
    # ═══════════════════════════════════════════════════════
    # 📝 معالجة النصوص
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """اقتصاص النص"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def remove_mentions(text: str) -> str:
        """إزالة المنشنات"""
        return re.sub(r'@\w+', '', text).strip()
    
    @staticmethod
    def remove_links(text: str) -> str:
        """إزالة الروابط"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text).strip()
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """استخراج الهاشتاجات"""
        return re.findall(r'#\w+', text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """استخراج المنشنات"""
        return re.findall(r'@\w+', text)
    
    @staticmethod
    def reverse_text(text: str) -> str:
        """عكس النص"""
        return text[::-1]
    
    # ═══════════════════════════════════════════════════════
    # ⏰ الوقت والتاريخ
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def get_current_time() -> datetime:
        """الوقت الحالي"""
        return datetime.now()
    
    @staticmethod
    def add_time(base_time: datetime, **kwargs) -> datetime:
        """إضافة وقت"""
        return base_time + timedelta(**kwargs)
    
    @staticmethod
    def is_time_between(current: datetime, start: datetime, end: datetime) -> bool:
        """التحقق إذا كان الوقت بين وقتين"""
        return start <= current <= end
    
    @staticmethod
    def get_age(birth_date: datetime) -> Dict[str, int]:
        """حساب العمر"""
        now = datetime.now()
        diff = now - birth_date
        
        years = diff.days // 365
        months = (diff.days % 365) // 30
        days = (diff.days % 365) % 30
        
        return {
            'years': years,
            'months': months,
            'days': days,
            'total_days': diff.days
        }
    
    # ═══════════════════════════════════════════════════════
    # 🎯 أدوات خاصة بالبوت
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def parse_command_args(text: str, expected_args: int = 0) -> Dict:
        """تحليل أمر مع arguments"""
        parts = text.split()
        
        result = {
            'command': parts[0] if parts else '',
            'args': parts[1:] if len(parts) > 1 else [],
            'full_text': ' '.join(parts[1:]) if len(parts) > 1 else ''
        }
        
        return result
    
    @staticmethod
    def create_mention(user_id: int, name: str) -> str:
        """إنشاء منشن"""
        return f'<a href="tg://user?id={user_id}">{name}</a>'
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """تجاوز رموز Markdown"""
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    @staticmethod
    def split_long_message(text: str, max_length: int = 4096) -> List[str]:
        """تقسيم رسالة طويلة"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        while len(text) > max_length:
            # البحث عن فقرة كاملة للتقسيم عندها
            split_at = text.rfind('\n\n', 0, max_length)
            if split_at == -1:
                split_at = text.rfind('\n', 0, max_length)
            if split_at == -1:
                split_at = max_length
            
            parts.append(text[:split_at])
            text = text[split_at:].strip()
        
        if text:
            parts.append(text)
        
        return parts
    
    # ═══════════════════════════════════════════════════════
    # 🎨 التنسيق والزخرفة
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def decorate_text(text: str, style: str = 'bold') -> str:
        """زخرفة النص"""
        styles = {
            'bold': f'**{text}**',
            'italic': f'_{text}_',
            'code': f'`{text}`',
            'underline': f'__{text}__',
            'strikethrough': f'~~{text}~~'
        }
        return styles.get(style, text)
    
    @staticmethod
    def create_progress_bar(current: int, total: int, length: int = 20) -> str:
        """إنشاء شريط تقدم"""
        if total == 0:
            return '□' * length
        
        filled = int((current / total) * length)
        bar = '■' * filled + '□' * (length - filled)
        percentage = Helpers.calculate_percentage(current, total)
        
        return f"{bar} {percentage}%"
    
    @staticmethod
    def get_random_emoji(category: str = 'general') -> str:
        """جلب إيموجي عشوائي"""
        emojis = {
            'general': ['😀', '😃', '😄', '😁', '😊', '🙂', '😉', '😌'],
            'happy': ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣'],
            'sad': ['😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖'],
            'money': ['💰', '💵', '💴', '💶', '💷', '💸', '🤑', '💳'],
            'fire': ['🔥', '⚡', '💥', '✨', '🌟', '💫', '⭐', '🌠'],
            'love': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍']
        }
        
        return random.choice(emojis.get(category, emojis['general']))

# ═══════════════════════════════════════════════════════
# 🚀 دوال سريعة (Shortcuts)
# ═══════════════════════════════════════════════════════

def clean(text: str) -> str:
    """اختصار لتنظيف النص"""
    return Helpers.clean_text(text)

def fmt_num(number: int) -> str:
    """اختصار لتنسيق الرقم"""
    return Helpers.format_number(number)

def fmt_time(minutes: int) -> str:
    """اختصار لتنسيق الوقت"""
    return Helpers.format_duration(minutes)

def rnd(items: List, count: int = 1):
    """اختصار للاختيار العشوائي"""
    return Helpers.pick_random(items, count)

def trunc(text: str, max_len: int = 100) -> str:
    """اختصار للاقتصاص"""
    return Helpers.truncate_text(text, max_len)
