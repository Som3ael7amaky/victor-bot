"""
فيكتور - معالج الترحيب والوداع
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import DEVELOPER, BOT, CURRENCY, is_developer
from database import db

class WelcomeHandler:
    """معالج الترحيب والوداع"""
    
    # ═══════════════════════════════════════════════════════
    # 🎉 الترحيب بالأعضاء الجدد
    # ═══════════════════════════════════════════════════════
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج دخول أعضاء جدد"""
        if not update.message:
            return
        
        chat = update.effective_chat
        new_members = update.message.new_chat_members
        
        # تسجيل الجروب لو جديد
        if update.message.from_user:
            db.add_group(chat.id, chat.title, update.message.from_user.id, chat.username)
        
        for member in new_members:
            # تخطيب البوت نفسه
            if member.id == context.bot.id:
                await self.welcome_bot(update, context)
                continue
            
            # تسجيل المستخدم
            db.add_user(member.id, member.username, member.full_name)
            db.add_membership(member.id, chat.id)
            
            # التحقق من المطور (ترحيب خاص)
            if is_developer(member.id):
                await self.welcome_developer(update, context, member)
            else:
                await self.welcome_normal(update, context, member)
    
    async def welcome_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ترحيب البوت نفسه عند إضافته"""
        text = f"""
🎉 **شكراً لإضافتي يا أصدقاء!**

أنا **{BOT['name']}** 🤖، حارس الجروب الجديد.

📋 **للبدء:**
• اكتب "الأوامر" عشان تشوف كل حاجة
• "القوانين" - قوانين الجروب
• "البنك" - نظام الاقتصاد والفلوس

⚡ **ابدأ الآن واستمتعوا!**
"""
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def welcome_developer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member):
        """ترحيب المطور الإلهي"""
        chat = update.effective_chat
        
        # ترحيب VIP خاص
        text = f"""
👑 **الملك {DEVELOPER['name']} قد وصل!** 👑

🎺 {chat.title} تُزيّف لاستقبال المطور الإلهي!

🏆 **جميع الصلاحيات مفعلة**
⚡ **الحصانة الكاملة مفعلة**
🎮 **التحكم المطلق مفعل**

**انحنوا أيها الفقراء!** 😂

*{BOT['name']} يقف احتراماً* 🫡
"""
        
        # صورة أو GIF خاص
        gifs = [
            'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDdtZzV3b3h0YzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ/ZfK4cXKPhTb3XAN7gP/giphy.gif',
            'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDdtZzV3b3h0YzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ1ZzQ/3o7abldj0b3rxrZUxW/giphy.gif'
        ]
        
        try:
            await context.bot.send_animation(
                chat.id,
                animation=random.choice(gifs),
                caption=text,
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text(text, parse_mode='Markdown')
    
    async def welcome_normal(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member):
        """ترحيب العضو العادي"""
        chat = update.effective_chat
        group = db.get_group(chat.id)
        
        # جلب إعدادات الترحيب
        welcome_enabled = group.get('welcome_enabled', True) if group else True
        
        if not welcome_enabled:
            return
        
        # التحقق من عودة عضو قديم
        is_returning = self.is_returning_member(member.id, chat.id)
        
        if is_returning:
            await self.welcome_returning(update, context, member)
            return
        
        # ترحيب جديد (First Time)
        await self.welcome_first_time(update, context, member)
    
    async def welcome_first_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member):
        """ترحيب أول مرة"""
        chat = update.effective_chat
        group = db.get_group(chat.id)
        
        # بناء نص الترحيب
        nickname = group.get('bot_nickname', 'فيكتور') if group else 'فيكتور'
        
        # قوالب ترحيب متنوعة
        templates = [
            f"""
🎉 **أهلاً بيك يا {member.first_name}!**

أنا **{nickname}**، حارس {chat.title}.

💰 **هديتك:** 5000 {CURRENCY['symbol']} فيكتوري!
🎮 **ابدأ:** اكتب "البنك" عشان تستلم هديتك

📋 **عشان تبدأ:**
• "الأوامر" - كل أوامري
• "القوانين" - قوانين الجروب
• "مساعدة" - لو محتاج مساعدة

**انضم لعيلتنا!** 🌟
""",
            f"""
👋 **يا هلا والله يا {member.first_name}!**

{chat.title} بتنور بوجودك!

🏆 **أنا {nickname}**، مساعدك الشخصي.
💸 **معاك 5000 {CURRENCY['symbol']}** هدية ترحيب!

🎯 **ابدأ مغامرتك:**
اكتب "البنك" واستلم فلوسك

**مستنينك!** 🚀
""",
            f"""
✨ **عضو جديد! مرحباً {member.first_name}!**

أهلاً بيك في **{chat.title}**!

🤖 **{nickname}** تحت أمرك:
• فلوس؟ اكتب "البنك"
• لعب؟ اكتب "لعبة"
• مساعدة؟ اكتب "مساعدة"

💰 **رصيدك الافتتاحي:** 5000 {CURRENCY['symbol']}

**يلا بينا!** 🎮
"""
        ]
        
        text = random.choice(templates)
        
        # أزرار تفاعلية
        keyboard = [
            [
                InlineKeyboardButton("🏦 البنك", callback_data=f'welcome_bank_{member.id}'),
                InlineKeyboardButton("📋 الأوامر", callback_data=f'welcome_cmds_{member.id}')
            ],
            [
                InlineKeyboardButton("⚖️ القوانين", callback_data=f'welcome_rules_{member.id}'),
                InlineKeyboardButton("🎮 العب", callback_data=f'welcome_play_{member.id}')
            ]
        ]
        
        # إرسال الترحيب
        try:
            # محاولة إرسال صورة أو GIF
            welcome_media = group.get('welcome_media') if group else None
            
            if welcome_media:
                if welcome_media.endswith('.gif') or 'gif' in welcome_media:
                    await context.bot.send_animation(
                        chat.id,
                        animation=welcome_media,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_photo(
                        chat.id,
                        photo=welcome_media,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
            else:
                # ترحيب نصي فقط
                await context.bot.send_message(
                    chat.id,
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            # fallback للنص فقط
            await context.bot.send_message(
                chat.id,
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # رسالة خاصة للعضو
        try:
            private_text = f"""
🎉 **أهلاً بيك في {chat.title}!**

أنا {BOT['name']}، وده تلخيص سريع:

🏦 **البنك:** اكتب "البنك" في الجروب
💰 **رصيدك:** 5000 {CURRENCY['symbol']}
🎮 **الألعاب:** "لعبة" أو "تحدي"

⚡ **نصيحة:** تفاعل كتير عشان تكسب فلوس أكتر!

**بالتوفيق!** 🚀
"""
            await context.bot.send_message(member.id, private_text, parse_mode='Markdown')
        except:
            pass  # العضو قفل الخاص
    
    async def welcome_returning(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member):
        """ترحيب عضو عائد"""
        chat = update.effective_chat
        
        templates = [
            f"رجعت تاني يا {member.first_name}! اشتقنالك 😊",
            f"يا هلا بالغالي {member.first_name}! وينك من زمان؟",
            f"{member.first_name} عاد! 🎉 الجروب نور بوجودك",
            f"شكلك نسيتنا يا {member.first_name}! 😂 أهلاً بيك"
        ]
        
        text = random.choice(templates)
        await context.bot.send_message(chat.id, text)
    
    # ═══════════════════════════════════════════════════════
    # 👋 الوداع
    # ═══════════════════════════════════════════════════════
    
    async def handle_left_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج خروج الأعضاء"""
        if not update.message:
            return
        
        chat = update.effective_chat
        left_member = update.message.left_chat_member
        
        # تخطي البوت نفسه
        if left_member.id == context.bot.id:
            return
        
        # تخطي المطور (ما يتودعش 😂)
        if is_developer(left_member.id):
            text = f"""
👑 **المطور {DEVELOPER['name']} غادر!**

الجروب فقد نوره... 😢

*سنعود أقوى* 💪
"""
            await update.message.reply_text(text, parse_mode='Markdown')
            return
        
        # تحديد سبب الخروج
        reason = self.detect_leave_reason(left_member.id, chat.id)
        
        # نص الوداع
        templates = {
            'left': [
                f"👋 {left_member.first_name} غادر الجروب. بالتوفيق!",
                f"🚶 {left_member.first_name} مشي. يارب نشوفه تاني!",
                f"😢 {left_member.first_name} سابنا. الله معاك!"
            ],
            'kicked': [
                f"🥾 {left_member.first_name} تم طرده من الجروب.",
                f"🚫 {left_member.first_name} اضطر يمشي.",
                f"⚠️ {left_member.first_name} مغادر قسراً."
            ],
            'banned': [
                f"🚷 {left_member.first_name} تم حظره نهائياً.",
                f"⛔ {left_member.first_name} ممنوع من العودة.",
                f"🚫 {left_member.first_name} في قائمة الممنوعين."
            ]
        }
        
        text = random.choice(templates.get(reason, templates['left']))
        
        # إحصائية
        group_stats = db.get_group_stats(chat.id)
        current_count = group_stats.get('members', 0) - 1
        
        text += f"\n\n📊 **الأعضاء الحاليون:** {max(0, current_count)}"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
        # تحديث قاعدة البيانات
        db.update_membership(left_member.id, chat.id, is_active=False)
    
    def detect_leave_reason(self, user_id: int, chat_id: int) -> str:
        """تحديد سبب الخروج"""
        # التحقق من وجود عقوبات حديثة
        recent_punishments = db.get_recent_punishments(user_id, chat_id, minutes=5)
        
        for p in recent_punishments:
            if p['type'] == 'ban':
                return 'banned'
            elif p['type'] == 'kick':
                return 'kicked'
        
        return 'left'
    
    # ═══════════════════════════════════════════════════════
    # 🛠 دوال مساعدة
    # ═══════════════════════════════════════════════════════
    
    def is_returning_member(self, user_id: int, chat_id: int) -> bool:
        """التحقق إذا كان عضو عائد"""
        # التحقق من وجود عضوية سابقة
        membership = db.get_membership(user_id, chat_id)
        if membership:
            join_date = membership.get('join_date')
            if join_date:
                # لو دخل قبل أكتر من يوم = عائد
                join_datetime = datetime.fromisoformat(join_date)
                return (datetime.now() - join_datetime).days > 1
        return False
    
    async def welcome_group_batch(self, update: Update, context: ContextTypes.DEFAULT_TYPE, members):
        """ترحيب جماعي (لو دخلوا كتار فوقت واحد)"""
        chat = update.effective_chat
        
        names = [m.first_name for m in members[:5]]  # أول 5 بس
        names_text = "، ".join(names)
        
        if len(members) > 5:
            names_text += f" و {len(members) - 5} آخرين"
        
        text = f"""
🎉 **أهلاً بالدفعة الجديدة!**

{names_text}

انضموا لـ {chat.title}!

💰 كل واحد معاه 5000 {CURRENCY['symbol']} هدية!
اكتبوا "البنك" عشان تستلموها.

**مرحباً بيكم!** 🌟
"""
        
        await context.bot.send_message(chat.id, text, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الترحيب"""
        query = update.callback_query
        data = query.data
        
        if data.startswith('welcome_bank_'):
            await query.answer("🏦 اكتب 'البنك' في الجروب!")
            await query.edit_message_reply_markup(None)
            
        elif data.startswith('welcome_cmds_'):
            text = """
📋 **الأوامر الأساسية:**

🏦 **البنك:** حالتي، راتبي، تحويل، متجر
🎮 **اللعب:** لعبة، تحدي، نكتة
🛠 **أدوات:** طقس، ترجم، احسب
⚙️ **عام:** القوانين، مساعدة

**جرب بنفسك!** 🚀
"""
            await query.answer()
            await query.edit_message_text(text, parse_mode='Markdown')
            
        elif data.startswith('welcome_rules_'):
            await query.answer("⚖️ اكتب 'القوانين' في الجروب!")
            
        elif data.startswith('welcome_play_'):
            games = ["🎮 XO", "🎯 تحدي", "🎲 حظ", "🏆 سباق"]
            text = f"**اختار لعبة:**\n\n" + "\n".join([f"• {g}" for g in games])
            await query.answer()
            await query.edit_message_text(text, parse_mode='Markdown')
