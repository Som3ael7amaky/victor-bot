"""
فيكتور - معالج الإدارة
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from config import DEVELOPER, TEXTS, is_developer
from database import db

class AdminHandler:
    """معالج أوامر الإدارة"""
    
    # ═══════════════════════════════════════════════════════
    # 🛠 أوامر الإدارة الأساسية
    # ═══════════════════════════════════════════════════════
    
    async def cmd_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حظر عضو"""
        if not await self.is_admin(update, context):
            return
        
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message
        
        # جلب العضو المستهدف
        target = await self.get_target_user(update, context)
        if not target:
            await message.reply_text("⚠️ حدد العضو بالرد أو المنشن")
            return
        
        # التحقق من الحصانة
        if is_developer(target['id']):
            await message.reply_text("⛔ لا يمكنك حظر المطور الإلهي!")
            return
        
        if target['id'] == user.id:
            await message.reply_text("🤔 مش هتحظر نفسك صح؟")
            return
        
        # جلب السبب والمدة
        args = context.args
        duration = None
        reason = "مخالفة القوانين"
        
        if args:
            # التحقق إذا كان أول argument رقم (مدة)
            if args[0].isdigit():
                duration = int(args[0])
                reason = ' '.join(args[1:]) if len(args) > 1 else reason
            else:
                reason = ' '.join(args)
        
        # تنفيذ الحظر
        db.ban_user(target['id'], chat.id, user.id, reason, duration)
        
        try:
            if duration:
                # بان مؤقت
                until = datetime.now() + timedelta(minutes=duration)
                await context.bot.ban_chat_member(
                    chat.id, target['id'],
                    until_date=until
                )
                time_text = self.format_duration(duration)
                text = f"🚷 تم حظر {target['mention']} لمدة {time_text}\nالسبب: {reason}"
            else:
                # بان دائم
                await context.bot.ban_chat_member(chat.id, target['id'])
                text = f"🚷 تم حظر {target['mention']} نهائياً\nالسبب: {reason}"
            
            await message.reply_text(text, parse_mode='Markdown')
            
            # إشعار المطور
            await self.notify_developer(
                context, 
                f"🚷 حظر جديد:\nالمحظور: {target['name']}\nالحاظر: {user.first_name}\nالسبب: {reason}"
            )
            
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فك حظر عضو"""
        if not await self.is_admin(update, context):
            return
        
        chat = update.effective_chat
        message = update.effective_message
        
        target = await self.get_target_user(update, context)
        if not target:
            # محاولة جلب من الـ ID
            if context.args:
                try:
                    user_id = int(context.args[0])
                    await context.bot.unban_chat_member(chat.id, user_id)
                    await message.reply_text("✅ تم فك الحظر")
                    return
                except:
                    pass
            await message.reply_text("⚠️ حدد العضو")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target['id'])
            db.update_user(target['id'], is_banned=False)
            await message.reply_text(f"✅ تم فك حظر {target['mention']}", parse_mode='Markdown')
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_mute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """كتم عضو"""
        if not await self.is_admin(update, context):
            return
        
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message
        
        target = await self.get_target_user(update, context)
        if not target:
            await message.reply_text("⚠️ حدد العضو")
            return
        
        if is_developer(target['id']):
            await message.reply_text("⛔ لا يمكنك كتم المطور!")
            return
        
        # جلب المدة (افتراضي 60 دقيقة)
        duration = 60
        if context.args:
            try:
                duration = int(context.args[0])
            except:
                pass
        
        db.mute_user(target['id'], chat.id, user.id, duration)
        
        try:
            await context.bot.restrict_chat_member(
                chat.id, target['id'],
                until_date=datetime.now() + timedelta(minutes=duration)
            )
            time_text = self.format_duration(duration)
            await message.reply_text(
                f"🔇 تم كتم {target['mention']} لمدة {time_text}",
                parse_mode='Markdown'
            )
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_unmute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فك كتم عضو"""
        if not await self.is_admin(update, context):
            return
        
        chat = update.effective_chat
        message = update.effective_message
        
        target = await self.get_target_user(update, context)
        if not target:
            await message.reply_text("⚠️ حدد العضو")
            return
        
        try:
            # إزالة القيود
            await context.bot.restrict_chat_member(
                chat.id, target['id'],
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            db.update_user(target['id'], is_muted=False, mute_until=None)
            await message.reply_text(f"🔊 تم فك كتم {target['mention']}", parse_mode='Markdown')
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_warn(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحذير عضو"""
        if not await self.is_admin(update, context):
            return
        
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message
        
        target = await self.get_target_user(update, context)
        if not target:
            await message.reply_text("⚠️ حدد العضو")
            return
        
        if is_developer(target['id']):
            await message.reply_text("⛔ لا يمكنك تحذير المطور!")
            return
        
        reason = ' '.join(context.args) if context.args else "مخالفة"
        
        # إضافة التحذير
        is_banned = db.warn_user(target['id'], chat.id, user.id, reason)
        
        # جلب عدد التحذيرات الحالي
        user_data = db.get_user(target['id'])
        warnings = user_data.get('warnings', 0)
        
        if is_banned:
            await message.reply_text(
                f"⚠️ {target['mention']} وصل لـ 3 تحذيرات وتم حظره تلقائياً!",
                parse_mode='Markdown'
            )
        else:
            await message.reply_text(
                f"⚠️ تحذير {warnings}/3 لـ {target['mention']}\nالسبب: {reason}",
                parse_mode='Markdown'
            )
    
    async def cmd_unwarn(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إزالة تحذير"""
        if not await self.is_admin(update, context):
            return
        
        message = update.effective_message
        target = await self.get_target_user(update, context)
        
        if not target:
            await message.reply_text("⚠️ حدد العضو")
            return
        
        # إزالة تحذير واحد
        user_data = db.get_user(target['id'])
        current_warnings = user_data.get('warnings', 0)
        
        if current_warnings > 0:
            db.update_user(target['id'], warnings=current_warnings - 1)
            await message.reply_text(
                f"✅ تم إزالة تحذير من {target['mention']}\nالآن: {current_warnings - 1}/3",
                parse_mode='Markdown'
            )
        else:
            await message.reply_text("ℹ️ العضو ليس لديه تحذيرات")
    
    async def cmd_kick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """طرد عضو"""
        if not await self.is_admin(update, context):
            return
        
        chat = update.effective_chat
        message = update.effective_message
        
        target = await self.get_target_user(update, context)
        if not target:
            await message.reply_text("⚠️ حدد العضو")
            return
        
        if is_developer(target['id']):
            await message.reply_text("⛔ لا يمكنك طرد المطور!")
            return
        
        try:
            await context.bot.ban_chat_member(chat.id, target['id'])
            await context.bot.unban_chat_member(chat.id, target['id'])  # فك الحظر للسماح بالعودة
            
            reason = ' '.join(context.args) if context.args else "طرد إداري"
            await message.reply_text(
                f"👢 تم طرد {target['mention']}\nالسبب: {reason}",
                parse_mode='Markdown'
            )
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_pin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تثبيت رسالة"""
        if not await self.is_admin(update, context):
            return
        
        message = update.effective_message
        
        if not message.reply_to_message:
            await message.reply_text("⚠️ رد على الرسالة اللي عايز تثبتها")
            return
        
        try:
            silent = 'silent' in context.args or 'هادي' in ' '.join(context.args)
            await message.reply_to_message.pin(disable_notification=silent)
            await message.reply_text("📌 تم التثبيت")
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_unpin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء تثبيت"""
        if not await self.is_admin(update, context):
            return
        
        chat = update.effective_chat
        
        try:
            if update.effective_message.reply_to_message:
                await update.effective_message.reply_to_message.unpin()
            else:
                await context.bot.unpin_all_chat_messages(chat.id)
            await update.effective_message.reply_text("📌 تم إلغاء التثبيت")
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حذف رسالة"""
        if not await self.is_admin(update, context):
            return
        
        message = update.effective_message
        
        if not message.reply_to_message:
            await message.reply_text("⚠️ رد على الرسالة اللي عايز تمسحها")
            return
        
        try:
            await message.reply_to_message.delete()
            await message.delete()  # حذف أمر الحذف أيضاً
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    async def cmd_purge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حذف مجموعة رسائل"""
        if not await self.is_admin(update, context):
            return
        
        message = update.effective_message
        
        if not message.reply_to_message:
            await message.reply_text("⚠️ رد على أول رسالة عايز تمسح منها")
            return
        
        try:
            # عدد الرسائل (افتراضي 10)
            count = 10
            if context.args:
                try:
                    count = min(int(context.args[0]), 100)  # حد أقصى 100
                except:
                    pass
            
            chat_id = message.chat_id
            start_message_id = message.reply_to_message.message_id
            
            deleted = 0
            for msg_id in range(start_message_id, start_message_id + count):
                try:
                    await context.bot.delete_message(chat_id, msg_id)
                    deleted += 1
                except:
                    pass
            
            await message.reply_text(f"🗑 تم حذف {deleted} رسالة")
            
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {str(e)}")
    
    # ═══════════════════════════════════════════════════════
    # 🛠 دوال مساعدة
    # ═══════════════════════════════════════════════════════
    
    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من الصلاحيات"""
        user = update.effective_user
        chat = update.effective_chat
        
        # المطور يتخطى كل شيء
        if is_developer(user.id):
            return True
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return True
            else:
                await update.effective_message.reply_text(TEXTS['errors']['no_permission'])
                return False
        except Exception as e:
            await update.effective_message.reply_text(f"❌ خطأ في التحقق: {str(e)}")
            return False
    
    async def get_target_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
        """جلب المستخدم المستهدف من الرد أو المنشن"""
        message = update.effective_message
        
        # محاولة الرد
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            return {
                'id': user.id,
                'username': user.username,
                'name': user.first_name,
                'mention': user.mention_html()
            }
        
        # محاولة المنشن من الـ args
        if context.args:
            username = context.args[0].replace('@', '')
            # هنا محتاج بحث في قاعدة البيانات
            # بس مؤقتاً نرجع None
            pass
        
        return None
    
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
    
    async def notify_developer(self, context: ContextTypes.DEFAULT_TYPE, text: str):
        """إشعار المطور"""
        try:
            await context.bot.send_message(DEVELOPER['id'], text)
        except:
            pass
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        data = query.data
        
        if data == 'admin_logs':
            # عرض سجلات الإدارة
            logs = db.get_logs('punishment', limit=10)
            text = "📋 آخر العقوبات:\n\n"
            for log in logs:
                text += f"• {log['action']} - {log['timestamp']}\n"
            await query.edit_message_text(text)
        
        elif data == 'admin_settings':
            # إعدادات الإدارة
            keyboard = [
                [InlineKeyboardButton("تفعيل الحماية", callback_data='admin_protect_on')],
                [InlineKeyboardButton("تعطيل الحماية", callback_data='admin_protect_off')]
            ]
            await query.edit_message_text(
                "⚙️ إعدادات الإدارة:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
