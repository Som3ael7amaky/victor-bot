"""
فيكتور - معالج الاقتصاد (البنك)
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import (
    DEVELOPER, CURRENCY, BANKS, JOBS, SHOP, 
    TAXES, TREASURES, MARRIAGE, is_developer,
    get_bank_by_id, get_job_by_id, get_shop_item,
    calculate_tax, get_currency_tier
)
from database import db

class EconomyHandler:
    """معالج الاقتصاد والبنك"""
    
    def __init__(self):
        self.active_games = {}  # الألعاب النشطة
    
    # ═══════════════════════════════════════════════════════
    # 💰 الأوامر الأساسية للبنك
    # ═══════════════════════════════════════════════════════
    
    async def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة المستخدم الاقتصادية"""
        user = update.effective_user
        chat = update.effective_chat
        
        # جلب البيانات
        economy = db.get_balance(user.id)
        user_data = db.get_user(user.id)
        
        if not economy:
            await update.message.reply_text("❌ خطأ في جلب البيانات")
            return
        
        # حساب إجمالي الثروة
        balance = economy.get('balance', 0)
        bank_balance = economy.get('bank_balance', 0)
        bank_id = economy.get('bank_id', 'victor')
        job_id = economy.get('job_id')
        
        # جلب الممتلكات
        properties = db.get_properties(user.id)
        properties_value = sum(p.get('current_value', 0) for p in properties)
        daily_income = sum(p.get('daily_income', 0) for p in properties)
        
        total_wealth = balance + bank_balance + properties_value
        
        # تحديد الفئة
        tier = get_currency_tier(total_wealth)
        
        # جلب الوظيفة
        job_text = "بدون وظيفة"
        if job_id:
            job = get_job_by_id(job_id)
            if job:
                job_text = f"{job['name']} (🏆 {job['salary']} يومياً)"
        
        # جلب البنك
        bank = get_bank_by_id(bank_id)
        bank_name = bank['name'] if bank else "غير معروف"
        
        # بناء الرسالة
        text = f"""
💰 **حالتك المالية يا {user.first_name}**

{tier['symbol']} **فئتك:** {tier['name']}

🏦 **البنك:** {bank_name}
💵 **نقدي:** {balance:,} {CURRENCY['symbol']}
🏛 **في البنك:** {bank_balance:,} {CURRENCY['symbol']}
🏠 **ممتلكاتك:** {properties_value:,} {CURRENCY['symbol']}
📊 **إجمالي ثروتك:** {total_wealth:,} {CURRENCY['symbol']}

💼 **وظيفتك:** {job_text}
📈 **دخلك اليومي:** {daily_income + economy.get('daily_income', 0):,} {CURRENCY['symbol']}

💳 **رقم حسابك:** `{user.id}`
"""
        
        # أزرار سريعة
        keyboard = [
            [
                InlineKeyboardButton("🏦 البنك", callback_data='eco_bank'),
                InlineKeyboardButton("💼 الوظيفة", callback_data='eco_job')
            ],
            [
                InlineKeyboardButton("🛒 المتجر", callback_data='eco_shop'),
                InlineKeyboardButton("💸 تحويل", callback_data='eco_transfer')
            ],
            [
                InlineKeyboardButton("🏆 التوب", callback_data='eco_leaderboard')
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def cmd_bank(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض تفاصيل البنك"""
        user = update.effective_user
        
        economy = db.get_balance(user.id)
        bank_id = economy.get('bank_id', 'victor')
        bank_balance = economy.get('bank_balance', 0)
        
        bank = get_bank_by_id(bank_id)
        
        if not bank:
            await update.message.reply_text("❌ خطأ في البيانات")
            return
        
        # حساب الفايدة المتوقعة
        monthly_interest = int(bank_balance * bank['interest_rate'])
        
        text = f"""
🏦 **{bank['name']}**

{bank['color']} **الشعار:** _{bank['slogan']}_

💰 **رصيدك:** {bank_balance:,} {CURRENCY['symbol']}
📈 **فائدة شهرية:** {monthly_interest:,} {CURRENCY['symbol']} ({bank['interest_rate']*100:.0f}%)
🔒 **الحماية:** {bank['protection']*100:.0f}%

✨ **المميزات:**
"""
        for feature in bank['features']:
            text += f"• {feature}\n"
        
        # أزرار العمليات
        keyboard = [
            [
                InlineKeyboardButton("📥 إيداع", callback_data='bank_deposit'),
                InlineKeyboardButton("📤 سحب", callback_data='bank_withdraw')
            ],
            [
                InlineKeyboardButton("🏦 تغيير البنك", callback_data='bank_change'),
                InlineKeyboardButton("📊 الفايدة", callback_data='bank_interest')
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def cmd_salary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """صرف الراتب"""
        user = update.effective_user
        
        economy = db.get_balance(user.id)
        job_id = economy.get('job_id')
        
        if not job_id:
            await update.message.reply_text(
                "❌ **ماعندكش وظيفة!**\n\n"
                "اكتب 'وظائف' عشان تشوف الوظائف المتاحة.",
                parse_mode='Markdown'
            )
            return
        
        # محاولة صرف الراتب
        salary = db.collect_salary(user.id)
        
        if salary == -1:
            # لسه بدري
            last = economy.get('last_salary')
            if last:
                last_time = datetime.fromisoformat(last)
                next_time = last_time + timedelta(hours=20)
                remaining = next_time - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                
                await update.message.reply_text(
                    f"⏳ **صبراً!**\n\n"
                    f"راتبك الصادر: {hours} ساعة و {minutes} دقيقة",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("⏳ **انتظر 20 ساعة بين كل راتب والتاني**")
        
        elif salary > 0:
            job = get_job_by_id(job_id)
            job_name = job['name'] if job else "وظيفتك"
            
            await update.message.reply_text(
                f"💰 **تم صرف راتبك!**\n\n"
                f"💼 {job_name}\n"
                f"💵 المبلغ: {salary:,} {CURRENCY['symbol']}\n\n"
                f"اكتب 'حالتي' عشان تشوف رصيدك الجديد.",
                parse_mode='Markdown'
            )
        
        else:
            await update.message.reply_text("❌ حدث خطأ، جرب تاني")
    
    async def cmd_transfer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحويل فلوس لمستخدم آخر"""
        user = update.effective_user
        message = update.effective_message
        
        # جلب المستلم والمبلغ
        if not message.reply_to_message and not context.args:
            await message.reply_text(
                "💸 **طريقة التحويل:**\n\n"
                "1. رد على رسالة الشخص واكتب: `تحويل 1000`\n"
                "2. أو اكتب: `تحويل @username 1000`",
                parse_mode='Markdown'
            )
            return
        
        # جلب المستلم
        target = None
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            target = {
                'id': target_user.id,
                'name': target_user.first_name,
                'mention': target_user.mention_html()
            }
        else:
            # من الـ args
            if len(context.args) < 2:
                await message.reply_text("⚠️ حدد المستخدم والمبلغ")
                return
            
            username = context.args[0].replace('@', '')
            # هنا محتاج بحث في قاعدة البيانات
            # مؤقتاً نرجع خطأ
            await message.reply_text("⚠️ استخدم الرد على الرسالة أسهل")
            return
        
        # جلب المبلغ
        try:
            if message.reply_to_message:
                amount = int(context.args[0]) if context.args else 0
            else:
                amount = int(context.args[1])
        except:
            await message.reply_text("⚠️ حدد مبلغ صحيح")
            return
        
        if amount <= 0:
            await message.reply_text("⚠️ المبلغ لازم يكون أكبر من صفر")
            return
        
        # التحقق من الرصيد
        economy = db.get_balance(user.id)
        if economy['balance'] < amount:
            await message.reply_text(
                f"❌ **فلوسك مش كفاية!**\n\n"
                f"محتاج: {amount:,} {CURRENCY['symbol']}\n"
                f"معاك: {economy['balance']:,} {CURRENCY['symbol']}",
                parse_mode='Markdown'
            )
            return
        
        # تنفيذ التحويل
        success = db.transfer_money(user.id, target['id'], amount, "تحويل يدوي")
        
        if success:
            await message.reply_text(
                f"✅ **تم التحويل بنجاح!**\n\n"
                f"💸 المبلغ: {amount:,} {CURRENCY['symbol']}\n"
                f"👤 إلى: {target['mention']}\n\n"
                f"اكتب 'حالتي' عشان تشوف رصيدك.",
                parse_mode='Markdown',
                parse_mode='HTML'
            )
            
            # إشعار المستلم
            try:
                await context.bot.send_message(
                    target['id'],
                    f"🎉 **وصلك تحويل!**\n\n"
                    f"من: {user.first_name}\n"
                    f"المبلغ: {amount:,} {CURRENCY['symbol']}\n\n"
                    f"اكتب 'حالتي' عشان تشوف رصيدك.",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        else:
            await message.reply_text("❌ فشل التحويل، جرب تاني")
    
    # ═══════════════════════════════════════════════════════
    # 🛒 المتجر
    # ═══════════════════════════════════════════════════════
    
    async def cmd_shop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المتجر"""
        text = f"""
🛒 **متجر {CURRENCY['name']}**

اختر قسم:
"""
        
        keyboard = []
        for key, category in SHOP.items():
            emoji = "🔧" if key == 'tools' else "🏠" if key == 'properties' else "🏢" if key == 'companies' else "🛡️" if key == 'insurance' else "💎"
            keyboard.append([
                InlineKeyboardButton(f"{emoji} {category['name']}", callback_data=f'shop_category_{key}')
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='eco_back')])
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def cmd_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شراء سلعة"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "🛒 **طريقة الشراء:**\n\n"
                "اكتب: `اشتري [كود السلعة]`\n\n"
                "مثال: `اشتري t1` (مكنسة سحرية)\n\n"
                "اكتب 'متجر' عشان تشوف السلع المتاحة.",
                parse_mode='Markdown'
            )
            return
        
        item_id = context.args[0].lower()
        item = get_shop_item(item_id)
        
        if not item:
            await update.message.reply_text("❌ السلعة غير موجودة، اكتب 'متجر' للقائمة")
            return
        
        # جلب الرصيد
        economy = db.get_balance(user.id)
        
        if economy['balance'] < item['price']:
            await update.message.reply_text(
                f"❌ **فلوسك مش كفاية!**\n\n"
                f"السلعة: {item['name']}\n"
                f"السعر: {item['price']:,} {CURRENCY['symbol']}\n"
                f"معاك: {economy['balance']:,} {CURRENCY['symbol']}",
                parse_mode='Markdown'
            )
            return
        
        # تحديد نوع السلعة
        item_type = None
        daily_income = 0
        for key, category in SHOP.items():
            for cat_item in category['items']:
                if cat_item['id'] == item_id:
                    item_type = key
                    daily_income = cat_item.get('daily_income', 0)
                    break
        
        # تنفيذ الشراء
        success = db.buy_item(user.id, item_id, item_type, item['price'], daily_income)
        
        if success:
            text = f"""
✅ **تم الشراء بنجاح!**

🛒 **{item['name']}**
💰 السعر: {item['price']:,} {CURRENCY['symbol']}

"""
            if 'effect' in item:
                text += f"✨ التأثير: {item['effect']}\n"
            if daily_income > 0:
                text += f"📈 الدخل اليومي: +{daily_income:,} {CURRENCY['symbol']}\n"
            
            text += "\nاكتب 'ممتلكاتي' عشان تشوف اللي اشتريته."
            
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ فشل الشراء، جرب تاني")
    
    async def cmd_properties(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض ممتلكات المستخدم"""
        user = update.effective_user
        
        properties = db.get_properties(user.id)
        
        if not properties:
            await update.message.reply_text(
                "🏠 **ماعندكش ممتلكات حالياً!**\n\n"
                "اكتب 'متجر' عشان تشتري.",
                parse_mode='Markdown'
            )
            return
        
        text = f"🏠 **ممتلكاتك يا {user.first_name}:**\n\n"
        
        total_value = 0
        total_income = 0
        
        for i, prop in enumerate(properties, 1):
            item = get_shop_item(prop['item_id'])
            name = item['name'] if item else prop['item_id']
            value = prop['current_value']
            income = prop.get('daily_income', 0)
            
            text += f"{i}. **{name}**\n"
            text += f"   💰 القيمة: {value:,} {CURRENCY['symbol']}\n"
            if income > 0:
                text += f"   📈 الدخل: {income:,}/يوم\n"
            text += "\n"
            
            total_value += value
            total_income += income
        
        text += f"\n📊 **الإجمالي:**\n"
        text += f"💰 القيمة: {total_value:,} {CURRENCY['symbol']}\n"
        text += f"📈 الدخل اليومي: {total_income:,} {CURRENCY['symbol']}"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 🎁 الكنوز
    # ═══════════════════════════════════════════════════════
    
    async def cmd_treasure(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """البحث عن كنز"""
        user = update.effective_user
        
        # التحقق من الحد اليومي
        if not db.can_find_treasure(user.id):
            await update.message.reply_text(
                "⏳ **استنى بكرة!**\n\n"
                "تقدر تدور على كنز مرتين بس في اليوم.",
                parse_mode='Markdown'
            )
            return
        
        # توليد الكنز
        treasure = self.generate_treasure()
        
        # إضافة للرصيد (أو خصم لو فخ)
        db.add_treasure(user.id, treasure['id'], treasure['amount'])
        
        # بناء الرسالة
        if treasure['id'] == 'trap':
            text = f"""
💩 **وقعت في فخ!**

خسرت: {abs(treasure['amount']):,} {CURRENCY['symbol']}

حظ أوفر المرة الجاية! 😅
"""
        else:
            text = f"""
{treaure['name']} **لقيت كنز!**

💰 المكافأة: {treasure['amount']:,} {CURRENCY['symbol']}

{'🎉 **مبروك! أنت المحظوظ!**' if treasure['id'] == 'victory' else 'حظ سعيد! 🍀'}
"""
        
        # عدد المحاولات المتبقية
        remaining = 2 - db.get_treasure_count_today(user.id)
        text += f"\n📊 محاولاتك المتبقية اليوم: {remaining}"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    def generate_treasure(self) -> dict:
        """توليد كنز عشوائي"""
        rand = random.random()
        cumulative = 0
        
        for treasure in TREASURES['types']:
            cumulative += treasure['probability']
            if rand <= cumulative:
                # توليد المبلغ
                if treasure['id'] == 'trap':
                    amount = -treasure['max']  # خسارة ثابتة
                else:
                    amount = random.randint(treasure['min'], treasure['max'])
                
                return {
                    'id': treasure['id'],
                    'name': treasure['name'],
                    'amount': amount
                }
        
        # افتراضي
        return {
            'id': 'bronze',
            'name': '🥉 برونزي',
            'amount': random.randint(100, 500)
        }
    
    # ═══════════════════════════════════════════════════════
    # 💍 الزواج
    # ═══════════════════════════════════════════════════════
    
    async def cmd_marry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الزواج"""
        user = update.effective_user
        message = update.effective_message
        
        # التحقق من عدم وجود زواج سابق
        existing = db.get_marriage(user.id)
        if existing:
            await message.reply_text(
                "❌ **أنت متزوج بالفعل!**\n\n"
                f"زوجتك: {existing['user2_id'] if existing['user1_id'] == user.id else existing['user1_id']}\n"
                "اكتب 'طلاق' لو عايز تطلق.",
                parse_mode='Markdown'
            )
            return
        
        # جلب الشريك
        if not message.reply_to_message:
            await message.reply_text(
                "💍 **طريقة الزواج:**\n\n"
                "1. رد على رسالة الشخص اللي عايز تتزوجه\n"
                "2. اكتب: `تزوج [المهر]`\n\n"
                "مثال: `تزوج 10000`",
                parse_mode='Markdown'
            )
            return
        
        partner = message.reply_to_message.from_user
        
        if partner.id == user.id:
            await message.reply_text("🤔 مش هتتزوج نفسك صح؟")
            return
        
        if partner.is_bot:
            await message.reply_text("🤖 البوتات ممنوع يتجوزوا!")
            return
        
        # جلب المهر
        try:
            dowry = int(context.args[0]) if context.args else 1000
        except:
            dowry = 1000
        
        # التحقق من المهر
        economy = db.get_balance(user.id)
        if economy['balance'] < dowry:
            await message.reply_text(
                f"❌ **فلوسك مش كفاية للمهر!**\n\n"
                f"المهر: {dowry:,} {CURRENCY['symbol']}\n"
                f"معاك: {economy['balance']:,} {CURRENCY['symbol']}",
                parse_mode='Markdown'
            )
            return
        
        # تحديد مستوى المهر
        dowry_level = 'فقير'
        for level in MARRIAGE['dowry']['levels']:
            if dowry >= level['amount']:
                dowry_level = level['name']
        
        # تنفيذ الزواج (بانتظار الموافقة في الواقع، لكن هنا مباشر)
        # في النظام الحقيقي محتاج موافقة الطرف الثاني
        
        success = db.marry(user.id, partner.id, dowry, dowry_level)
        
        if success:
            # خصم المهر
            db.update_balance(user.id, -dowry, 'marriage_dowry', f'مهر لـ {partner.first_name}')
            
            text = f"""
💍 **تم الزواج بنجاح!**

👰 {user.mention_html()} + 🤵 {partner.mention_html()}

💰 المهر: {dowry:,} {CURRENCY['symbol']} ({dowry_level})
🎉 مبروك للعروسين!

📈 **فوائد الزواج:**
• دخل مضاعف
• هدايا شهرية
• مشاركة الممتلكات
""",
            await message.reply_text(text, parse_mode='HTML')
        else:
            await message.reply_text("❌ فشل الزواج، الطرف التاني متزوج؟")
    
    async def cmd_divorce(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الطلاق"""
        user = update.effective_user
        
        marriage = db.get_marriage(user.id)
        
        if not marriage:
            await update.message.reply_text("❌ **أنت مش متزوج!**")
            return
        
        # حساب غرامة الطلاق
        economy = db.get_balance(user.id)
        partner_id = marriage['user2_id'] if marriage['user1_id'] == user.id else marriage['user1_id']
        
        # في النظام الحقيقي محتوب نسبة من الأغنى
        penalty = int(economy['balance'] * MARRIAGE['divorce_penalty'])
        
        db.divorce(marriage['id'], "طلاق بالتراضي")
        
        text = f"""
💔 **تم الطلاق**

غرامة الطلاق: {penalty:,} {CURRENCY['symbol']}

حظ أوفر في المرة الجاية! 🙏
"""
        await update.message.reply_text(text, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 🏆 التوبات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض التوب"""
        category = 'balance'
        
        if context.args:
            arg = context.args[0].lower()
            if arg in ['غني', 'اغنى', 'فلوس']:
                category = 'balance'
            elif arg in ['ثروة', 'اجمالي']:
                category = 'richest'
        
        leaders = db.get_leaderboard(category, 10)
        
        text = f"🏆 **توب الأغنياء - {CURRENCY['name']}**\n\n"
        
        medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        for i, leader in enumerate(leaders, 0):
            name = leader.get('full_name') or leader.get('username') or f"مستخدم {leader['user_id']}"
            value = leader.get('balance') or leader.get('total_wealth', 0)
            
            text += f"{medals[i]} **{name}**\n"
            text += f"   💰 {value:,} {CURRENCY['symbol']}\n\n"
        
        # موقع المستخدم الحالي
        user = update.effective_user
        user_economy = db.get_balance(user.id)
        user_total = user_economy['balance'] + user_economy['bank_balance']
        
        text += f"---\n📊 **أنت:** {user_total:,} {CURRENCY['symbol']}"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 🔘 معالج الأزرار
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الاقتصاد"""
        query = update.callback_query
        data = query.data
        
        if data == 'eco_bank':
            await self.cmd_bank(update, context)
        
        elif data == 'eco_job':
            await self.show_jobs(update, context)
        
        elif data == 'eco_shop':
            await self.cmd_shop(update, context)
        
        elif data == 'eco_transfer':
            await query.answer("💸 اكتب: تحويل @username المبلغ")
        
        elif data == 'eco_leaderboard':
            await self.cmd_leaderboard(update, context)
        
        elif data.startswith('shop_category_'):
            category = data.replace('shop_category_', '')
            await self.show_category(update, context, category)
        
        elif data == 'bank_deposit':
            await query.answer("📥 اكتب: ادفع [المبلغ]")
        
        elif data == 'bank_withdraw':
            await query.answer("📤 اكتب: اسحب [المبلغ]")
    
    async def show_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الوظائف المتاحة"""
        text = "💼 **الوظائف المتاحة:**\n\n"
        
        for job in JOBS[:10]:  # أول 10 بس للاختصار
            text += f"{job['name']}\n"
            text += f"   💰 {job['salary']:,} {CURRENCY['symbol']}/يوم\n"
            text += f"   ⏱️ يحتاج {job['days_required']} يوم عمل\n\n"
        
        text += "\nاكتب 'قدم على [رقم الوظيفة]' للتقديم"
        
        await update.callback_query.edit_message_text(text, parse_mode='Markdown')
    
    async def show_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
        """عرض قسم من المتجر"""
        if category not in SHOP:
            return
        
        cat = SHOP[category]
        text = f"🛒 **{cat['name']}**\n\n"
        
        for item in cat['items']:
            text += f"**{item['name']}** (`{item['id']}`)\n"
            text += f"💰 السعر: {item['price']:,} {CURRENCY['symbol']}\n"
            
            if 'effect' in item:
                text += f"✨ {item['effect']}\n"
            if 'daily_income' in item:
                text += f"📈 +{item['daily_income']:,}/يوم\n"
            
            text += "\n"
        
        text += "اكتب `اشتري [الكود]` للشراء"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='eco_shop')]]
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def handle_shop_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار المتجر"""
        query = update.callback_query
        data = query.data
        
        if data.startswith('buy_'):
            item_id = data.replace('buy_', '')
            # تنفيذ الشراء
            pass
