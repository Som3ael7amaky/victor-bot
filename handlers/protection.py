"""
فيكتور - معالج الحماية (الحصن)
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ContextTypes

from config import DEVELOPER, PROTECTION, is_developer
from database import db

class ProtectionHandler:
    """معالج الحماية والفلاتر"""
    
    def __init__(self):
        self.spam_tracker = {}  # تتبع السبام
        self.message_cache = {}  # كاش الرسائل
        self.bad_words = self.load_bad_words()
    
    # ═══════════════════════════════════════════════════════
    # 🛡 الفحص الرئيسي للرسائل
    # ═══════════════════════════════════════════════════════
    
    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        فحص الرسالة ضد كل الفلاتر
        ترجع True لو تم حذف/معاقبة، False لو سليمة
        """
        if not update.message or not update.message.text:
            return False
        
        user = update.effective_user
        chat = update.effective_chat
        text = update.message.text
        
        # المطور يتخطى كل الفلاتر
        if is_developer(user.id):
            return False
        
        # ═══════════════════════════════════════════════════
        # 1. فلتر الروابط
        # ═══════════════════════════════════════════════════
        
        if await self.check_links(update, context, text):
            return True
        
        # ═══════════════════════════════════════════════════
        # 2. فلتر المنشنات
        # ═══════════════════════════════════════════════════
        
        if await self.check_mentions(update, context, text):
            return True
        
        # ═══════════════════════════════════════════════════
        # 3. فلتر السبام (تكرار)
        # ═══════════════════════════════════════════════════
        
        if await self.check_spam(update, context, user.id, chat.id, text):
            return True
        
        # ═══════════════════════════════════════════════════
        # 4. فلتر الكلمات الممنوعة
        # ═══════════════════════════════════════════════════
        
        if await self.check_bad_words(update, context, text):
            return True
        
        # ═══════════════════════════════════════════════════
        # 5. فلتر التوجيه (Forward)
        # ═══════════════════════════════════════════════════
        
        if await self.check_forward(update, context):
            return True
        
        # ═══════════════════════════════════════════════════
        # 6. فلتر الحسابات الجديدة
        # ═══════════════════════════════════════════════════
        
        if await self.check_new_account(update, context, user):
            return True
        
        return False  # الرسالة سليمة
    
    # ═══════════════════════════════════════════════════════
    # 🔗 فلتر الروابط
    # ═══════════════════════════════════════════════════════
    
    async def check_links(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
        """التحقق من الروابط"""
        if not PROTECTION['filters']['links']['enabled']:
            return False
        
        # أنماط الروابط
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r't\.me/\w+',
            r'telegram\.me/\w+',
            r'@\w+',  # يوزر تليجرام
        ]
        
        found_links = []
        for pattern in url_patterns:
            matches = re.findall(pattern, text)
            found_links.extend(matches)
        
        if not found_links:
            return False
        
        # التحقق من القائمة البيضاء
        whitelist = PROTECTION['filters']['links'].get('whitelist', [])
        for link in found_links[:]:
            domain = urlparse(link).netloc if 'http' in link else link
            if any(w in domain for w in whitelist):
                found_links.remove(link)
        
        if not found_links:
            return False
        
        # تم العثور على رابط ممنوع
        action = PROTECTION['filters']['links']['action']
        
        if action == 'delete_warn':
            await self.delete_and_warn(update, context, "إرسال روابط ممنوعة")
        elif action == 'delete':
            await update.message.delete()
        elif action == 'mute':
            await self.mute_user(update, context, 60, "روابط")
        
        return True
    
    # ═══════════════════════════════════════════════════════
    # 📢 فلتر المنشنات
    # ═══════════════════════════════════════════════════════
    
    async def check_mentions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
        """التحقق من المنشنات الجماعية"""
        if not PROTECTION['filters']['mentions']['enabled']:
            return False
        
        # عدد المنشنات
        mentions = re.findall(r'@\w+', text)
        all_mentions = len(mentions)
        
        # منشنات جماعية (@all, @everyone)
        spam_mentions = ['@all', '@everyone', '@here']
        has_spam_mention = any(m in text.lower() for m in spam_mentions)
        
        max_mentions = PROTECTION['filters']['mentions']['max_mentions']
        
        if all_mentions > max_mentions or has_spam_mention:
            action = PROTECTION['filters']['mentions']['action']
            
            if 'mute' in action:
                duration = int(action.split('_')[1]) if '_' in action else 60
                await self.mute_user(update, context, duration, "منشنات مزعجة")
            else:
                await self.delete_and_warn(update, context, "منشنات جماعية")
            
            return True
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 🔄 فلتر السبام (التكرار)
    # ═══════════════════════════════════════════════════════
    
    async def check_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                        user_id: int, chat_id: int, text: str) -> bool:
        """التحقق من السبام والتكرار"""
        if not PROTECTION['filters']['spam']['enabled']:
            return False
        
        key = f"{user_id}_{chat_id}"
        now = datetime.now()
        
        # تنظيف الكاش القديم
        if key in self.spam_tracker:
            self.spam_tracker[key] = [
                msg for msg in self.spam_tracker[key]
                if (now - msg['time']).seconds < 60
            ]
        else:
            self.spam_tracker[key] = []
        
        # إضافة الرسالة الحالية
        self.spam_tracker[key].append({
            'text': text,
            'time': now,
            'message_id': update.message.message_id
        })
        
        messages = self.spam_tracker[key]
        
        # فحص 1: عدد الرسائل في الدقيقة
        max_messages = PROTECTION['filters']['spam']['max_messages']
        if len(messages) > max_messages:
            await self.mute_user(update, context, 360, "سبام - رسائل كتيرة")
            return True
        
        # فحص 2: نفس النص المتكرر
        if len(messages) >= 3:
            last_three = [m['text'] for m in messages[-3:]]
            if len(set(last_three)) == 1:  # نفس النص 3 مرات
                await self.mute_user(update, context, 360, "سبام - تكرار نفس النص")
                return True
        
        # فحص 3: رسائل سريعة جداً (بوت؟)
        if len(messages) >= 5:
            times = [m['time'] for m in messages[-5:]]
            avg_time = sum((times[i+1] - times[i]).seconds for i in range(4)) / 4
            if avg_time < 2:  # أقل من 2 ثانية بين كل رسالة
                await self.mute_user(update, context, 720, "سبام مشبوه - سرعة غير طبيعية")
                return True
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 🤬 فلتر الكلمات الممنوعة
    # ═══════════════════════════════════════════════════════
    
    async def check_bad_words(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
        """التحقق من الكلمات الممنوعة"""
        if not PROTECTION['filters']['bad_words']['enabled']:
            return False
        
        text_lower = text.lower()
        
        # فحص الكلمات الممنوعة
        for word in self.bad_words:
            if word in text_lower:
                action = PROTECTION['filters']['bad_words']['action']
                
                if action == 'delete_warn':
                    await self.delete_and_warn(update, context, "استخدام كلمات ممنوعة")
                elif action == 'delete':
                    await update.message.delete()
                elif action == 'mute':
                    await self.mute_user(update, context, 30, "كلمات ممنوعة")
                
                return True
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 📤 فلتر التوجيه (Forward)
    # ═══════════════════════════════════════════════════════
    
    async def check_forward(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من الرسائل الموجهة"""
        if not PROTECTION['filters']['forwards']['enabled']:
            return False
        
        if update.message.forward_from or update.message.forward_from_chat:
            action = PROTECTION['filters']['forwards']['action']
            
            if action == 'delete':
                await update.message.delete()
                return True
            elif action == 'delete_warn':
                await self.delete_and_warn(update, context, "إرسال رسائل موجهة")
                return True
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 👶 فلتر الحسابات الجديدة
    # ═══════════════════════════════════════════════════════
    
    async def check_new_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user) -> bool:
        """التحقق من حسابات جديدة مشبوهة"""
        # التحقق من تاريخ إنشاء الحساب (لو متاح)
        # ملاحظة: Telegram API لا يعطي تاريخ الإنشاء مباشرة
        # لكن ممكن نحلل من ID المستخدم (تقريبي)
        
        # الحسابات اللي ID بتاعها كبير = جديدة
        # هذا تقريبي فقط
        if user.id > 2000000000:  # حساب نسبياً جديد
            # ممكن نضيف تحقق إضافي
            pass
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 🌙 الوضع الهادئ (Silent Mode)
    # ═══════════════════════════════════════════════════════
    
    async def check_silent_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من الوضع الهادئ"""
        chat = update.effective_chat
        group = db.get_group(chat.id)
        
        if not group:
            return False
        
        silent_start = group.get('silent_mode_start')
        silent_end = group.get('silent_mode_end')
        
        if not silent_start or not silent_end:
            return False
        
        now = datetime.now().strftime('%H:%M')
        
        # التحقق من الوقت
        if self.is_time_in_range(now, silent_start, silent_end):
            user = update.effective_user
            
            # التحقق من الصلاحيات
            try:
                member = await context.bot.get_chat_member(chat.id, user.id)
                if member.status in ['administrator', 'creator']:
                    return False  # الأدمنز يتخطوا
            except:
                pass
            
            # حذف الرسالة
            await update.message.delete()
            
            # إشعار خاص (مرة واحدة)
            key = f"silent_notice_{user.id}_{chat.id}"
            if key not in self.message_cache:
                self.message_cache[key] = True
                try:
                    await context.bot.send_message(
                        user.id,
                        f"⏰ الجروب في **الوضع الهادئ** الآن ({silent_start} - {silent_end}).\n"
                        f"جرب تكتب بعدين!",
                        parse_mode='Markdown'
                    )
                except:
                    pass
            
            return True
        
        return False
    
    # ═══════════════════════════════════════════════════════
    # 🛠 دوال العقوبات
    # ═══════════════════════════════════════════════════════
    
    async def delete_and_warn(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
        """حذف الرسالة وتحذير المستخدم"""
        message = update.message
        user = update.effective_user
        chat = update.effective_chat
        
        # حذف الرسالة
        try:
            await message.delete()
        except:
            pass
        
        # تحذير
        is_banned = db.warn_user(user.id, chat.id, None, reason)
        
        # إشعار
        try:
            if is_banned:
                await context.bot.send_message(
                    chat.id,
                    f"⚠️ {user.mention_html()} وصل لـ 3 تحذيرات وتم حظره!\n"
                    f"السبب: {reason}",
                    parse_mode='HTML'
                )
            else:
                user_data = db.get_user(user.id)
                warnings = user_data.get('warnings', 0)
                
                await context.bot.send_message(
                    chat.id,
                    f"⚠️ {user.mention_html()} تحذير {warnings}/3\n"
                    f"السبب: {reason}",
                    parse_mode='HTML'
                )
        except:
            pass
    
    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       duration: int, reason: str):
        """كتم مستخدم"""
        user = update.effective_user
        chat = update.effective_chat
        
        # كتم في قاعدة البيانات
        db.mute_user(user.id, chat.id, None, duration)
        
        # كتم في تليجرام
        try:
            until = datetime.now() + timedelta(minutes=duration)
            await context.bot.restrict_chat_member(
                chat.id, user.id,
                until_date=until
            )
            
            # إشعار
            time_text = self.format_duration(duration)
            await context.bot.send_message(
                chat.id,
                f"🔇 {user.mention_html()} تم كتمه لمدة {time_text}\n"
                f"السبب: {reason}",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Error muting: {e}")
    
    # ═══════════════════════════════════════════════════════
    # 🛠 دوال مساعدة
    # ═══════════════════════════════════════════════════════
    
    def load_bad_words(self) -> list:
        """تحميل قائمة الكلمات الممنوعة"""
        # قائمة افتراضية، ممكن تتعدل من الإعدادات
        default_bad_words = [
            'سب', 'قذف', ' insult', ' bad word',
            # أضف المزيد حسب احتياجاتك
        ]
        
        # ممكن تحميل من ملف أو قاعدة بيانات
        return default_bad_words
    
    def is_time_in_range(self, current: str, start: str, end: str) -> bool:
        """التحقق إذا كان الوقت في النطاق"""
        current_time = datetime.strptime(current, '%H:%M')
        start_time = datetime.strptime(start, '%H:%M')
        end_time = datetime.strptime(end, '%H:%M')
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # يمر منتصف الليل (مثلاً 22:00 إلى 06:00)
            return current_time >= start_time or current_time <= end_time
    
    def format_duration(self, minutes: int) -> str:
        """تنسيق المدة"""
        if minutes < 60:
            return f"{minutes} دقيقة"
        elif minutes < 1440:
            hours = minutes // 60
            return f"{hours} ساعة"
        else:
            days = minutes // 1440
            return f"{days} يوم"
    
    async def add_bad_word(self, word: str):
        """إضافة كلمة ممنوعة"""
        if word not in self.bad_words:
            self.bad_words.append(word.lower())
            # حفظ في قاعدة البيانات
            # db.add_bad_word(word)
    
    async def remove_bad_word(self, word: str):
        """إزالة كلمة ممنوعة"""
        if word.lower() in self.bad_words:
            self.bad_words.remove(word.lower())
