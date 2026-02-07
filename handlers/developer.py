"""
فيكتور - معالج المطور (التحكم الإلهي)
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import DEVELOPER, BOT, CURRENCY, is_developer
from database import db

class DeveloperHandler:
    """معالج أوامر المطور الإلهية"""
    
    # ═══════════════════════════════════════════════════════
    # 👑 التحقق من المطور
    # ═══════════════════════════════════════════════════════
    
    async def check_developer(self, update: Update) -> bool:
        """التحقق من أن المستخدم هو المطور"""
        user = update.effective_user
        
        if not is_developer(user.id):
            await update.message.reply_text(
                "⛔ **هذا الأمر للمطور فقط!**\n\n"
                "أنت مش {DEVELOPER['title']} 😎",
                parse_mode='Markdown'
            )
            return False
        return True
    
    # ═══════════════════════════════════════════════════════
    # 🎛 لوحة التحكم الإلهية
    # ═══════════════════════════════════════════════════════
    
    async def cmd_developer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لوحة تحكم المطور"""
        if not await self.check_developer(update):
            return
        
        text = f"""
👑 **لوحة التحكم الإلهية**

مرحباً يا {DEVELOPER['name']}!

🤖 **البوت:** {BOT['name']} v{BOT['version']}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ **الأوامر السريعة:**
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 الإحصائيات", callback_data='dev_stats')],
            [InlineKeyboardButton("📢 بث للكل", callback_data='dev_broadcast')],
            [InlineKeyboardButton("💰 إعطاء فلوس", callback_data='dev_give')],
            [InlineKeyboardButton("🚫 بان عام", callback_data='dev_global_ban')],
            [InlineKeyboardButton("⚙️ إعدادات البوت", callback_data='dev_settings')],
            [InlineKeyboardButton("📋 سجلات النظام", callback_data='dev_logs')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════════
    # 📊 الإحصائيات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إحصائيات شاملة"""
        if not await self.check_developer(update):
            return
        
        # جلب الإحصائيات من قاعدة البيانات
        stats = self.get_full_stats()
        
        text = f"""
📊 **إحصائيات {BOT['name']} الشاملة**

👥 **المستخدمين:**
• إجمالي المستخدمين: {stats['total_users']:,}
• المستخدمين النشطين: {stats['active_users']:,}
• المحظورين: {stats['banned_users']:,}

🏘 **الجروبات:**
• إجمالي الجروبات: {stats['total_groups']:,}
• الجروبات النشطة: {stats['active_groups']:,}

💰 **الاقتصاد:**
• إجمالي الفلوس المتداولة: {stats['total_money']:,} {CURRENCY['symbol']}
• أغنى مستخدم: {stats['richest_user']}
• إجمالي المعاملات: {stats['total_transactions']:,}

🎮 **الألعاب:**
• الألعاب النشطة: {stats['active_games']}
• إجمالي الكنوز الم found: {stats['total_treasures']:,}

⚡ **الأداء:**
• سرعة الاستجابة: {stats['response_time']}ms
• uptime: {stats['uptime']}
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    def get_full_stats(self):
        """جلب الإحصائيات الكاملة"""
        # في الواقع هذي بتجي من قاعدة البيانات
        return {
            'total_users': 1500,
            'active_users': 320,
            'banned_users': 15,
            'total_groups': 45,
            'active_groups': 38,
            'total_money': 25000000,
            'richest_user': 'Unknown',
            'total_transactions': 8500,
            'active_games': 12,
            'total_treasures': 4500,
            'response_time': 120,
            'uptime': '5 days, 3 hours'
        }
    
    async def cmd_full_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إحصائيات مفصلة (للأمر السريع)"""
        await self.cmd_stats(update, context)
    
    # ═══════════════════════════════════════════════════════
    # 📢 البث والإشعارات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إرسال رسالة لكل الجروبات"""
        if not await self.check_developer(update):
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text(
                "📢 **طريقة البث:**\n\n"
                "1. اكتب الرسالة بعد الأمر: `/broadcast مرحباً للجميع!`\n"
                "2. أو رد على رسالة وأكتب `/broadcast`",
                parse_mode='Markdown'
            )
            return
        
        # جلب الرسالة
        if update.message.reply_to_message:
            message = update.message.reply_to_message
            text = message.text or message.caption or "📢 إشعار"
            entities = message.entities or message.caption_entities
        else:
            text = ' '.join(context.args)
            entities = None
        
        # تأكيد قبل الإرسال
        confirm_text = f"""
📢 **تأكيد البث**

الرسالة:
{text[:200]}{'...' if len(text) > 200 else ''}

هل أنت متأكد من الإرسال للجميع؟
"""
        
        keyboard = [[
            InlineKeyboardButton("✅ نعم، أرسل", callback_data='dev_broadcast_confirm'),
            InlineKeyboardButton("❌ إلغاء", callback_data='dev_cancel')
        ]]
        
        # حفظ الرسالة مؤقتاً
        context.user_data['broadcast_message'] = text
        context.user_data['broadcast_entities'] = entities
        
        await update.message.reply_text(
            confirm_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def execute_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنفيذ البث"""
        query = update.callback_query
        
        text = context.user_data.get('broadcast_message', '📢 إشعار')
        entities = context.user_data.get('broadcast_entities')
        
        # جلب كل الجروبات
        groups = db.get_all_groups()
        
        sent = 0
        failed = 0
        
        await query.edit_message_text("⏳ جاري الإرسال...", parse_mode='Markdown')
        
        for group in groups:
            try:
                await context.bot.send_message(
                    group['group_id'],
                    text,
                    entities=entities,
                    parse_mode='Markdown' if not entities else None
                )
                sent += 1
                await asyncio.sleep(0.1)  # تجنب الحظر
            except Exception as e:
                failed += 1
        
        await query.edit_message_text(
            f"✅ **تم الإرسال!**\n\n"
            f"📤 نجح: {sent}\n"
            f"❌ فشل: {failed}",
            parse_mode='Markdown'
        )
    
    async def cmd_quick_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بث سريع (للأمر النصي)"""
        await self.cmd_broadcast(update, context)
    
    # ═══════════════════════════════════════════════════════
    # 💰 التحكم في الاقتصاد
    # ═══════════════════════════════════════════════════════
    
    async def cmd_give_money(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعطاء فلوس لمستخدم"""
        if not await self.check_developer(update):
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "💰 **طريقة الإعطاء:**\n\n"
                "`/give @username 10000`\n"
                "أو بالرد: `/give 10000`",
                parse_mode='Markdown'
            )
            return
        
        # جلب المستخدم والمبلغ
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
            try:
                amount = int(context.args[0])
            except:
                await update.message.reply_text("⚠️ حدد مبلغ صحيح")
                return
        else:
            await update.message.reply_text("⚠️ استخدم الرد على الرسالة")
            return
        
        # إعطاء الفلوس
        db.update_balance(target.id, amount, 'developer_gift', f'هدية من {DEVELOPER["name"]}')
        
        await update.message.reply_text(
            f"💰 **تم الإعطاء!**\n\n"
            f"المستلم: {target.mention_html()}\n"
            f"المبلغ: {amount:,} {CURRENCY['symbol']}",
            parse_mode='HTML'
        )
        
        # إشعار المستلم
        try:
            await context.bot.send_message(
                target.id,
                f"🎁 **مفاجأة من {DEVELOPER['title']}!**\n\n"
                f"تم إضافة {amount:,} {CURRENCY['symbol']} لحسابك!\n\n"
                f"اكتب 'حالتي' عشان تشوف رصيدك.",
                parse_mode='Markdown'
            )
        except:
            pass
    
    # ═══════════════════════════════════════════════════════
    # 🚫 الحظر العام
    # ═══════════════════════════════════════════════════════
    
    async def cmd_global_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حظر مستخدم من كل الجروبات"""
        if not await self.check_developer(update):
            return
        
        if not update.message.reply_to_message and not context.args:
            await update.message.reply_text(
                "🚫 **الحظر العام:**\n\n"
                "رد على رسالة المستخدم واكتب: `/globalban [السبب]`",
                parse_mode='Markdown'
            )
            return
        
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        
        if not target:
            await update.message.reply_text("⚠️ حدد المستخدم")
            return
        
        reason = ' '.join(context.args) if context.args else "حظر عام إداري"
        
        # حظر من كل الجروبات
        groups = db.get_all_groups()
        banned_count = 0
        
        for group in groups:
            try:
                await context.bot.ban_chat_member(group['group_id'], target.id)
                banned_count += 1
            except:
                pass
        
        # تسجيل في قاعدة البيانات
        db.ban_user(target.id, None, DEVELOPER['id'], reason, None)  # None للبان العام
        
        await update.message.reply_text(
            f"🚫 **تم الحظر العام!**\n\n"
            f"المستخدم: {target.mention_html()}\n"
            f"السبب: {reason}\n"
            f"عدد الجروبات: {banned_count}",
            parse_mode='HTML'
        )
    
    # ═══════════════════════════════════════════════════════
    # ⚙️ إعدادات البوت
    # ═══════════════════════════════════════════════════════
    
    async def cmd_bot_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعدادات البوت"""
        if not await self.check_developer(update):
            return
        
        keyboard = [
            [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data='dev_restart')],
            [InlineKeyboardButton("📥 تحديث من GitHub", callback_data='dev_update')],
            [InlineKeyboardButton("💾 نسخة احتياطية", callback_data='dev_backup')],
            [InlineKeyboardButton("🔧 وضع الصيانة", callback_data='dev_maintenance')]
        ]
        
        await update.message.reply_text(
            "⚙️ **إعدادات البوت:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════════
    # 📋 السجلات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض سجلات النظام"""
        if not await self.check_developer(update):
            return
        
        logs = db.get_logs(limit=20)
        
        text = "📋 **آخر السجلات:**\n\n"
        
        for log in logs:
            text += f"• [{log['timestamp']}] {log['action']}\n"
        
        await update.message.reply_text(text[:4000], parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 🔘 معالج الأزرار
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار المطور"""
        query = update.callback_query
        
        if not is_developer(query.from_user.id):
            await query.answer("⛔ ممنوع!", show_alert=True)
            return
        
        data = query.data
        
        if data == 'dev_stats':
            await self.cmd_stats(update, context)
        
        elif data == 'dev_broadcast':
            await query.answer("📢 اكتب: /broadcast [الرسالة]")
        
        elif data == 'dev_broadcast_confirm':
            await self.execute_broadcast(update, context)
        
        elif data == 'dev_give':
            await query.answer("💰 اكتب: /give @user المبلغ")
        
        elif data == 'dev_global_ban':
            await query.answer("🚫 اكتب: /globalban @user")
        
        elif data == 'dev_settings':
            await self.cmd_bot_settings(update, context)
        
        elif data == 'dev_logs':
            await self.cmd_logs(update, context)
        
        elif data == 'dev_cancel':
            await query.edit_message_text("❌ تم الإلغاء", parse_mode='Markdown')
        
        elif data == 'dev_restart':
            await query.edit_message_text("🔄 جاري إعادة التشغيل...", parse_mode='Markdown')
            # هنا نفذ إعادة التشغيل
        
        elif data == 'dev_backup':
            await query.edit_message_text("💾 جاري النسخ الاحتياطي...", parse_mode='Markdown')
            # هنا نفذ النسخ
