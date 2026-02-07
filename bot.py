"""
فيكتور - الملف الرئيسي
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ═══════════════════════════════════════════════════════════
# 📥 استيراد الإعدادات والقاعدة
# ═══════════════════════════════════════════════════════════

from config import (
    BOT, DEVELOPER, SETTINGS, CURRENCY, TEXTS,
    is_developer, get_currency_tier
)
from database import db

# ═══════════════════════════════════════════════════════════
# 📥 استيراد المعالجات (Handlers)
# ═══════════════════════════════════════════════════════════

from handlers.admin import AdminHandler
from handlers.welcome import WelcomeHandler
from handlers.protection import ProtectionHandler
from handlers.economy import EconomyHandler
from handlers.tools import ToolsHandler
from handlers.fun import FunHandler
from handlers.developer import DeveloperHandler

# ═══════════════════════════════════════════════════════════
# 🔧 إعدادات اللوج
# ═══════════════════════════════════════════════════════════

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('victor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# 🤖 كلاس البوت الرئيسي
# ═══════════════════════════════════════════════════════════

class VictorBot:
    def __init__(self):
        self.token = BOT['token']
        self.name = BOT['name']
        self.version = BOT['version']
        
        # تهيئة المعالجات
        self.admin = AdminHandler()
        self.welcome = WelcomeHandler()
        self.protection = ProtectionHandler()
        self.economy = EconomyHandler()
        self.tools = ToolsHandler()
        self.fun = FunHandler()
        self.dev = DeveloperHandler()
        
        # تهيئة التطبيق
        self.application = Application.builder().token(self.token).build()
        
        self.setup_handlers()
    
    # ═══════════════════════════════════════════════════════
    # 🔌 إعداد المعالجات (Handlers Setup)
    # ═══════════════════════════════════════════════════════
    
    def setup_handlers(self):
        """إعداد جميع المعالجات"""
        
        # ═══════════════════════════════════════════════════
        # 1. معالجات الأوامر (Commands)
        # ═══════════════════════════════════════════════════
        
        # أوامر البداية
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        
        # أوامر المطور (أولوية قصوى)
        self.application.add_handler(CommandHandler("dev", self.dev.cmd_developer))
        self.application.add_handler(CommandHandler("stats", self.dev.cmd_stats))
        self.application.add_handler(CommandHandler("broadcast", self.dev.cmd_broadcast))
        
        # أوامر الإدارة
        self.application.add_handler(CommandHandler("ban", self.admin.cmd_ban))
        self.application.add_handler(CommandHandler("unban", self.admin.cmd_unban))
        self.application.add_handler(CommandHandler("mute", self.admin.cmd_mute))
        self.application.add_handler(CommandHandler("unmute", self.admin.cmd_unmute))
        self.application.add_handler(CommandHandler("warn", self.admin.cmd_warn))
        self.application.add_handler(CommandHandler("unwarn", self.admin.cmd_unwarn))
        self.application.add_handler(CommandHandler("kick", self.admin.cmd_kick))
        self.application.add_handler(CommandHandler("pin", self.admin.cmd_pin))
        self.application.add_handler(CommandHandler("unpin", self.admin.cmd_unpin))
        self.application.add_handler(CommandHandler("del", self.admin.cmd_delete))
        self.application.add_handler(CommandHandler("purge", self.admin.cmd_purge))
        
        # أوامر الإعدادات
        self.application.add_handler(CommandHandler("settings", self.cmd_settings))
        self.application.add_handler(CommandHandler("rules", self.cmd_rules))
        
        # ═══════════════════════════════════════════════════
        # 2. معالجات الرسائل النصية (Text Messages)
        # ═══════════════════════════════════════════════════
        
        # معالج عام للرسائل (للحماية والردود)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text),
            group=1  # أولوية عالية للحماية
        )
        
        # ═══════════════════════════════════════════════════
        # 3. معالجات الأعضاء الجدد (Members)
        # ═══════════════════════════════════════════════════
        
        self.application.add_handler(
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome.handle_new_member)
        )
        self.application.add_handler(
            MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, self.welcome.handle_left_member)
        )
        
        # ═══════════════════════════════════════════════════
        # 4. معالجات الأزرار (Callback Queries)
        # ═══════════════════════════════════════════════════
        
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # ═══════════════════════════════════════════════════
        # 5. معالج الأخطاء (Errors)
        # ═══════════════════════════════════════════════════
        
        self.application.add_error_handler(self.error_handler)
    
    # ═══════════════════════════════════════════════════════
    # ⚡ معالجات الأوامر الأساسية
    # ═══════════════════════════════════════════════════════
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user
        chat = update.effective_chat
        
        # تسجيل المستخدم
        db.add_user(user.id, user.username, user.full_name)
        
        # لو خاص (Private)
        if chat.type == 'private':
            await self.send_private_start(update, context)
        else:
            # لو جروب
            await self.send_group_start(update, context)
    
    async def send_private_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رسالة البداية في الخاص"""
        user = update.effective_user
        
        # التحقق من المطور
        if is_developer(user.id):
            text = f"""
👑 **أهلاً يا المطور الإلهي {DEVELOPER['name']}!**

أنا **{BOT['name']}**، البوت الخارق اللي بنيته.

🎛 **لوحة التحكم الإلهية:**
• /dev - أوامر المطور الكاملة
• /stats - إحصائيات كل الجروبات
• /broadcast - رسالة للجميع

⚡ **حالة البوت:** شغال بنجاح
🏆 **الإصدار:** {BOT['version']}
📅 **تاريخ البناء:** {BOT['build_date']}
"""
        else:
            text = f"""
🎉 **أهلاً بيك يا {user.first_name}!**

أنا **{BOT['name']}** 🤖، مساعدك الشخصي في الجروبات.

💡 **إزاي تستخدمني:**
• ضيفني لجروبك
• اكتب **"الأوامر"** عشان تشوف كل حاجة
• اكتب **"مساعدة"** لو محتاج مساعدة

🏆 **عملتي:** {CURRENCY['name']} {CURRENCY['symbol']}
🎮 **ألعابي:** بنك، ألغاز، تحديات

📌 **ابدأ الآن:** ضيفني لجروب واكتب "ابدأ"
"""
        
        keyboard = [
            [InlineKeyboardButton("➕ ضفني لجروبك", url=f"https://t.me/{BOT['username']}?startgroup=true")],
            [InlineKeyboardButton("📢 قناة التحديثات", url="https://t.me/")],
            [InlineKeyboardButton("💬 الدعم الفني", url=f"https://t.me/{DEVELOPER['username'].replace('@', '')}")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def send_group_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رسالة البداية في الجروب"""
        user = update.effective_user
        chat = update.effective_chat
        
        # تسجيل الجروب
        db.add_group(chat.id, chat.title, user.id, chat.username)
        
        text = f"""
🎉 **أهلاً بيكم في {chat.title}!**

أنا **{BOT['name']}** 🤖، جاهز أخدمكم.

📋 **للبدء اكتبوا:**
• **"الأوامر"** - كل أوامري
• **"القوانين"** - قوانين الجروب
• **"البنك"** - نظام الاقتصاد

👑 **المطور:** {DEVELOPER['name']}
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        text = """
📚 **أوامر فيكتور الأساسية:**

🏛 **الإدارة:**
ban, unban, mute, unmute, warn, unwarn, kick, pin, unpin, del, purge

🏦 **البنك:**
حالتي، بنكي، راتبي، تحويل، متجر، اشتري، ممتلكاتي

🎮 **التسلية:**
نكتة، لعبة، تحدي، صفع، حضن

🛠 **الأدوات:**
طقس، ترجم، احسب، سعر، معلومات

⚙️ **الإعدادات:**
settings, rules

👑 **المطور فقط:**
dev, stats, broadcast

💡 **أو اكتب أي حاجة بالعربي وسأساعدك!**
"""
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعدادات الجروب"""
        user = update.effective_user
        chat = update.effective_chat
        
        # التحقق من الصلاحيات
        if not await self.is_admin(user.id, chat.id, context):
            await update.message.reply_text("⛔ معندكش صلاحية.")
            return
        
        # جلب الإعدادات الحالية
        group = db.get_group(chat.id)
        
        text = f"""
⚙️ **إعدادات {chat.title}:**

🎭 **اسم البوت:** {group.get('bot_nickname', 'فيكتور')}
👋 **الترحيب:** {'مفعل' if group.get('welcome_enabled') else 'معطل'}
🛡 **الحماية:** {'مفعلة' if group.get('is_protected') else 'معطلة'}
🌙 **الوضع الهادئ:** {group.get('silent_mode_start', 'معطل')}

📋 **للتعديل:**
• تغيير الاسم: "سمي فيكتور [الاسم الجديد]"
• تعديل الترحيب: "عدل الترحيب [النص]"
• تفعيل/تعطيل: "الترحيب تشغيل" أو "الترحيب إيقاف"
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def cmd_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قوانين الجروب"""
        chat = update.effective_chat
        group = db.get_group(chat.id)
        
        rules = group.get('rules_text') if group else None
        
        if not rules:
            rules = """
📜 **القوانين العامة:**

1️⃣ احترام الجميع
2️⃣ ممنوع السب والقذف
3️⃣ ممنوع الروابط بدون إذن
4️⃣ ممنوع السبام
5️⃣ استمتعوا! 😊
"""
        
        await update.message.reply_text(rules, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 💬 معالج الرسائل النصية (القلب النابض)
    # ═══════════════════════════════════════════════════════
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج كل الرسائل النصية"""
        if not update.message or not update.message.text:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        text = update.message.text.strip()
        
        # تسجيل المستخدم والنشاط
        db.add_user(user.id, user.username, user.full_name)
        db.update_user(user.id, last_seen=datetime.now())
        
        # ═══════════════════════════════════════════════════
        # 1. التحقق من الحظر (Ban)
        # ═══════════════════════════════════════════════════
        
        user_data = db.get_user(user.id)
        if user_data and user_data.get('is_banned'):
            await update.message.delete()
            return
        
        # ═══════════════════════════════════════════════════
        # 2. التحقق من الكتم (Mute)
        # ═══════════════════════════════════════════════════
        
        if user_data and user_data.get('is_muted'):
            mute_until = user_data.get('mute_until')
            if mute_until and datetime.now() < datetime.fromisoformat(mute_until):
                await update.message.delete()
                return
            else:
                # رفع الكتم تلقائياً
                db.update_user(user.id, is_muted=False, mute_until=None)
        
        # ═══════════════════════════════════════════════════
        # 3. الحماية (Protection)
        # ═══════════════════════════════════════════════════
        
        is_spam = await self.protection.check_message(update, context)
        if is_spam:
            return  # تم حذف الرسالة أو معاقبة المستخدم
        
        # ═══════════════════════════════════════════════════
        # 4. معالجة الأوامر بالعربي (Text Commands)
        # ═══════════════════════════════════════════════════
        
        response = await self.process_arabic_command(update, context, text.lower())
        if response:
            return  # تم معالجة الأمر
        
        # ═══════════════════════════════════════════════════
        # 5. الردود الذكية (Smart Replies)
        # ═══════════════════════════════════════════════════
        
        await self.send_smart_reply(update, context, text)
    
    async def process_arabic_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
        """معالجة الأوامر بالعربي"""
        user = update.effective_user
        chat = update.effective_chat
        
        # ═══════════════════════════════════════════════════
        # 🏦 أوامر البنك
        # ═══════════════════════════════════════════════════
        
        if any(word in text for word in ['حالتي', 'فلوسي', 'رصيدي']):
            await self.economy.cmd_balance(update, context)
            return True
        
        if any(word in text for word in ['بنكي', 'حسابي البنكي']):
            await self.economy.cmd_bank(update, context)
            return True
        
        if 'راتبي' in text or 'معاشي' in text:
            await self.economy.cmd_salary(update, context)
            return True
        
        if 'تحويل' in text or 'ابعت فلوس' in text:
            await self.economy.cmd_transfer(update, context)
            return True
        
        if any(word in text for word in ['متجر', 'سوق', 'اشترى']):
            await self.economy.cmd_shop(update, context)
            return True
        
        if any(word in text for word in ['اشتري', 'شراء']):
            await self.economy.cmd_buy(update, context)
            return True
        
        if any(word in text for word in ['ممتلكاتي', 'أملاكي', 'شريت ايه']):
            await self.economy.cmd_properties(update, context)
            return True
        
        if 'كنز' in text or 'ادور' in text:
            await self.economy.cmd_treasure(update, context)
            return True
        
        if 'توب' in text or 'الأغنياء' in text or 'الأفضل' in text:
            await self.economy.cmd_leaderboard(update, context)
            return True
        
        # ═══════════════════════════════════════════════════
        # 💍 أوامر الزواج
        # ═══════════════════════════════════════════════════
        
        if 'تزوج' in text or 'جواز' in text:
            await self.economy.cmd_marry(update, context)
            return True
        
        if 'طلاق' in text:
            await self.economy.cmd_divorce(update, context)
            return True
        
        # ═══════════════════════════════════════════════════
        # 🛠 أوامر الأدوات
        # ═══════════════════════════════════════════════════
        
        if 'طقس' in text or 'الجو' in text:
            await self.tools.cmd_weather(update, context)
            return True
        
        if 'ترجم' in text:
            await self.tools.cmd_translate(update, context)
            return True
        
        if 'احسب' in text or 'حساب' in text:
            await self.tools.cmd_calculator(update, context)
            return True
        
        if 'سعر' in text or 'تحويل عملة' in text:
            await self.tools.cmd_currency(update, context)
            return True
        
        if 'معلومات' in text or 'عن' in text:
            await self.tools.cmd_info(update, context)
            return True
        
        # ═══════════════════════════════════════════════════
        # 🎮 أوامر التسلية
        # ═══════════════════════════════════════════════════
        
        if 'نكتة' in text or 'اضحك' in text or 'هزار' in text:
            await self.fun.cmd_joke(update, context)
            return True
        
        if any(word in text for word in ['لعبة', 'اكس او', 'حجر ورقة']):
            await self.fun.cmd_game(update, context)
            return True
        
        if 'تحدي' in text:
            await self.fun.cmd_challenge(update, context)
            return True
        
        if 'صفع' in text:
            await self.fun.cmd_slap(update, context)
            return True
        
        if 'حضن' in text:
            await self.fun.cmd_hug(update, context)
            return True
        
        # ═══════════════════════════════════════════════════
        # 📋 أوامر عامة
        # ═══════════════════════════════════════════════════
        
        if any(word in text for word in ['الأوامر', 'اوامر', 'مساعدة', 'help']):
            await self.cmd_help(update, context)
            return True
        
        if any(word in text for word in ['القوانين', 'قوانين', 'rules']):
            await self.cmd_rules(update, context)
            return True
        
        if any(word in text for word in ['الإعدادات', 'اعدادات', 'settings']):
            await self.cmd_settings(update, context)
            return True
        
        # ═══════════════════════════════════════════════════
        # 👑 أوامر المطور (خاصة)
        # ═══════════════════════════════════════════════════
        
        if is_developer(user.id):
            if 'توب المطور' in text or 'احصائياتي' in text:
                await self.dev.cmd_full_stats(update, context)
                return True
            
            if 'ارسل للكل' in text or 'بث' in text:
                await self.dev.cmd_quick_broadcast(update, context)
                return True
        
        return False  # لم يتم التعرف على الأمر
    
    async def send_smart_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """ردود ذكية على رسائل عادية"""
        user = update.effective_user
        
        # ردود على التحيات
        if any(word in text for word in ['صباح', 'صباح الخير', 'صباح النور']):
            replies = [
                f"صباح النور يا {user.first_name}! ☀️",
                f"صباح الفل يا {user.first_name}! 🌅",
                "صباح الورد! 🌹"
            ]
            await update.message.reply_text(replies[hash(user.id) % len(replies)])
            return
        
        if any(word in text for word in ['مساء', 'مساء الخير']):
            replies = [
                f"مساء النور يا {user.first_name}! 🌙",
                f"مساء الفل يا {user.first_name}! ✨",
                "مساء الورد! 🌹"
            ]
            await update.message.reply_text(replies[hash(user.id) % len(replies)])
            return
        
        # رد على اسم فيكتور
        if 'فيكتور' in text:
            if 'بحبك' in text or 'اعشقك' in text:
                await update.message.reply_text("🥺 أنا كمان... بس متقولش لحد!")
            elif 'كرهك' in text or 'مش بحبك' in text:
                await update.message.reply_text("💔 ليه كده؟ أنا باجتهد عشانكم!")
            else:
                await update.message.reply_text("نعم؟ أنا هنا! 🤖")
            return
        
        # رد على الشكر
        if any(word in text for word in ['شكرا', 'شكراً', 'thanks', 'thank you']):
            await update.message.reply_text("العفو! 🌟 في خدمتك دايماً!")
            return
    
    # ═══════════════════════════════════════════════════════
    # 🔘 معالج الأزرار (Callback Queries)
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج ضغطات الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # توجيع الـ Callback للمعالج المناسب
        if data.startswith('bank_'):
            await self.economy.handle_callback(update, context)
        elif data.startswith('shop_'):
            await self.economy.handle_shop_callback(update, context)
        elif data.startswith('game_'):
            await self.fun.handle_callback(update, context)
        elif data.startswith('admin_'):
            await self.admin.handle_callback(update, context)
        elif data.startswith('dev_'):
            await self.dev.handle_callback(update, context)
        else:
            await query.edit_message_text("⚠️ أمر غير معروف")
    
    # ═══════════════════════════════════════════════════════
    # 🛠 دوال مساعدة
    # ═══════════════════════════════════════════════════════
    
    async def is_admin(self, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من كون المستخدم أدمن"""
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False
    
    async def is_owner(self, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من كون المستخدم مالك"""
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status == 'creator'
        except:
            return False
    
    # ═══════════════════════════════════════════════════════
    # ❌ معالج الأخطاء
    # ═══════════════════════════════════════════════════════
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"Error: {context.error}")
        
        # تسجيل الخطأ
        db.add_log('error', str(context.error), 
                   update.effective_user.id if update else None,
                   update.effective_chat.id if update else None)
        
        # إشعار المطور
        try:
            await context.bot.send_message(
                chat_id=DEVELOPER['id'],
                text=f"⚠️ خطأ في البوت:\n{context.error}"
            )
        except:
            pass
    
    # ═══════════════════════════════════════════════════════
    # 🚀 تشغيل البوت
    # ═══════════════════════════════════════════════════════
    
    def run(self):
        """تشغيل البوت"""
        print(f"🤖 {self.name} v{self.version} يبدأ العمل...")
        print(f"👑 المطور: {DEVELOPER['name']}")
        print(f"🏆 العملة: {CURRENCY['name']}")
        
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

# ═══════════════════════════════════════════════════════════
# 🚀 نقطة البداية
# ═══════════════════════════════════════════════════════════

def main():
    """الدالة الرئيسية"""
    bot = VictorBot()
    bot.run()

if __name__ == '__main__':
    main()
