"""
فيكتور - معالج الأدوات
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import re
import random
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import SETTINGS

class ToolsHandler:
    """معالج الأدوات والمعلومات"""
    
    def __init__(self):
        self.weather_cache = {}
        self.translation_cache = {}
    
    # ═══════════════════════════════════════════════════════
    # 🌤 الطقس
    # ═══════════════════════════════════════════════════════
    
    async def cmd_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة الطقس"""
        if not context.args:
            await update.message.reply_text(
                "🌤 **طريقة الاستخدام:**\n\n"
                "اكتب: `طقس [اسم المدينة]`\n\n"
                "مثال: `طقس القاهرة` أو `طقس دبي`",
                parse_mode='Markdown'
            )
            return
        
        city = ' '.join(context.args)
        
        # محاولة جلب من الكاش
        cache_key = f"{city}_{datetime.now().strftime('%H')}"
        if cache_key in self.weather_cache:
            weather = self.weather_cache[cache_key]
        else:
            # محاكاة بيانات الطقس (لأننا مش معانا API حقيقي)
            weather = self.simulate_weather(city)
            self.weather_cache[cache_key] = weather
        
        emoji = self.get_weather_emoji(weather['condition'])
        
        text = f"""
{emoji} **طقس {city}**

🌡 **درجة الحرارة:** {weather['temp']}°C
💧 **الرطوبة:** {weather['humidity']}%
💨 **الرياح:** {weather['wind']} كم/س
👁 **الرؤية:** {weather['visibility']} كم

{weather['advice']}
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    def simulate_weather(self, city: str) -> dict:
        """محاكاة بيانات الطقس"""
        # في الواقع هنا نستخدم OpenWeatherMap API
        conditions = ['مشمس', 'غائم', 'ممطر', 'عاصف']
        weights = [0.5, 0.3, 0.15, 0.05]
        condition = random.choices(conditions, weights)[0]
        
        temps = {
            'مشمس': (25, 40),
            'غائم': (15, 28),
            'ممطر': (10, 22),
            'عاصف': (8, 20)
        }
        
        temp_range = temps[condition]
        temp = random.randint(temp_range[0], temp_range[1])
        
        advices = {
            'مشمس': '😎 يوم جميل، تمشى براحتك!',
            'غائم': '☁️ يوم معتدل، مثالي للخروج',
            'ممطر': '☔ خد مظلة معاك!',
            'عاصف': '💨 خليك في البيت لو تقدر'
        }
        
        return {
            'temp': temp,
            'condition': condition,
            'humidity': random.randint(30, 90),
            'wind': random.randint(5, 40),
            'visibility': random.randint(5, 10),
            'advice': advices[condition]
        }
    
    def get_weather_emoji(self, condition: str) -> str:
        """إيموجي حسب حالة الطقس"""
        emojis = {
            'مشمس': '☀️',
            'غائم': '☁️',
            'ممطر': '🌧️',
            'عاصف': '💨'
        }
        return emojis.get(condition, '🌤️')
    
    # ═══════════════════════════════════════════════════════
    # 🌐 الترجمة
    # ═══════════════════════════════════════════════════════
    
    async def cmd_translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ترجمة نص"""
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text(
                "🌐 **طريقة الترجمة:**\n\n"
                "1. رد على رسالة واكتب: `ترجم`\n"
                "2. أو اكتب: `ترجم [النص]`\n\n"
                "مثال: `ترجم hello world`",
                parse_mode='Markdown'
            )
            return
        
        # جلب النص
        if update.message.reply_to_message:
            text = update.message.reply_to_message.text
        else:
            text = ' '.join(context.args)
        
        if not text:
            await update.message.reply_text("⚠️ مفيش نص للترجمة")
            return
        
        # كشف اللغة (مبسط)
        is_english = bool(re.search(r'[a-zA-Z]', text))
        
        if is_english:
            # ترجمة من إنجليزي لعربي (محاكاة)
            translated = self.simulate_translation(text, 'en', 'ar')
            source_lang = 'الإنجليزية'
            target_lang = 'العربية'
        else:
            # ترجمة من عربي لإنجليزي (محاكاة)
            translated = self.simulate_translation(text, 'ar', 'en')
            source_lang = 'العربية'
            target_lang = 'الإنجليزية'
        
        result = f"""
🌐 **الترجمة**

من: {source_lang}
إلى: {target_lang}

📝 **الأصل:**
{text[:200]}

✅ **الترجمة:**
{translated[:500]}
"""
        
        await update.message.reply_text(result, parse_mode='Markdown')
    
    def simulate_translation(self, text: str, from_lang: str, to_lang: str) -> str:
        """محاكاة الترجمة"""
        # في الواقع هنا نستخدم Google Translate API
        # مؤقتاً نرجع نص توضيحي
        
        if from_lang == 'en':
            # قاموس بسيط للكلمات الشائعة
            dictionary = {
                'hello': 'مرحباً',
                'world': 'العالم',
                'how are you': 'كيف حالك',
                'thank you': 'شكراً',
                'good morning': 'صباح الخير',
                'good night': 'تصبح على خير',
                'i love you': 'أحبك',
                'welcome': 'أهلاً وسهلاً',
                'money': 'فلوس',
                'victor': 'فيكتور'
            }
            
            text_lower = text.lower()
            for en, ar in dictionary.items():
                text_lower = text_lower.replace(en, ar)
            
            return text_lower if text_lower != text.lower() else f"[ترجمة: {text}]"
        
        else:
            # عربي لإنجليزي
            dictionary = {
                'مرحبا': 'Hello',
                'شكرا': 'Thank you',
                'كيف حالك': 'How are you',
                'صباح الخير': 'Good morning',
                'فلوس': 'Money',
                'فيكتور': 'Victor'
            }
            
            for ar, en in dictionary.items():
                if ar in text:
                    text = text.replace(ar, en)
            
            return text if any(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in text) else f"[Translation: {text}]"
    
    # ═══════════════════════════════════════════════════════
    # 🧮 الحاسبة
    # ═══════════════════════════════════════════════════════
    
    async def cmd_calculator(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حاسبة علمية"""
        if not context.args:
            await update.message.reply_text(
                "🧮 **الحاسبة العلمية**\n\n"
                "اكتب: `احسب [المعادلة]`\n\n"
                "**العمليات:**\n"
                "• الجمع: `+`\n"
                "• الطرح: `-`\n"
                "• الضرب: `*`\n"
                "• القسمة: `/`\n"
                "• الأس: `**` أو `^`\n\n"
                "مثال: `احسب 15 * 8 + 32`",
                parse_mode='Markdown'
            )
            return
        
        expression = ' '.join(context.args)
        
        # تنظيف المعادلة
        expression = expression.replace('×', '*').replace('÷', '/')
        expression = expression.replace('^', '**')
        expression = expression.replace(' ', '')
        
        # التحقق من الأمان (منع أكواد ضارة)
        allowed_chars = set('0123456789+-*/.()** ')
        if not all(c in allowed_chars for c in expression):
            await update.message.reply_text("⚠️ معادلة غير صالحة")
            return
        
        try:
            # حساب النتيجة
            result = eval(expression)
            
            # تنسيق النتيجة
            if isinstance(result, float):
                result = round(result, 4)
            
            text = f"""
🧮 **الحاسبة**

📥 **المعادلة:**
`{expression}`

✅ **النتيجة:**
**{result:,}**
"""
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الحساب: {str(e)}")
    
    # ═══════════════════════════════════════════════════════
    # 💱 تحويل العملات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحويل العملات"""
        if not context.args:
            await update.message.reply_text(
                "💱 **تحويل العملات**\n\n"
                "اكتب: `سعر [المبلغ] [من] إلى [إلى]`\n\n"
                "مثال:\n"
                "`سعر 100 دولار إلى جنيه`\n"
                "`سعر 50 يورو إلى ريال`",
                parse_mode='Markdown'
            )
            return
        
        # محاكاة أسعار العملات
        rates = {
            'دولار': 30.90,      # USD to EGP
            'جنيه': 1,           # EGP
            'ريال': 8.24,        # SAR to EGP
            'درهم': 8.41,        # AED to EGP
            'دينار': 101.20,     # KWD to EGP
            'يورو': 33.50,       # EUR to EGP
            'جنيه_استرليني': 39.20,  # GBP to EGP
            'فيكتوري': 1000      # Victory to EGP
        }
        
        text = ' '.join(context.args).lower()
        
        # استخراج المبلغ
        amount_match = re.search(r'(\d+)', text)
        if not amount_match:
            await update.message.reply_text("⚠️ حدد المبلغ")
            return
        
        amount = int(amount_match.group(1))
        
        # استخراج العملات
        from_curr = None
        to_curr = None
        
        for curr in rates.keys():
            if curr in text:
                if not from_curr:
                    from_curr = curr
                elif not to_curr:
                    to_curr = curr
                    break
        
        if not from_curr or not to_curr:
            # افتراضي: دولار لجنيه
            from_curr = from_curr or 'دولار'
            to_curr = to_curr or 'جنيه'
        
        # التحويل
        from_rate = rates.get(from_curr, 1)
        to_rate = rates.get(to_curr, 1)
        
        result = (amount * from_rate) / to_rate
        
        text = f"""
💱 **تحويل العملات**

💰 **المبلغ:** {amount:,} {from_curr}
🔄 **السعر:** 1 {from_curr} = {from_rate/to_rate:.2f} {to_curr}

✅ **النتيجة:**
**{result:,.2f} {to_curr}**

📊 *الأسعار تقريبية وقد تتغير*
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # ℹ️ معلومات عامة
    # ═══════════════════════════════════════════════════════
    
    async def cmd_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معلومات عامة"""
        if not context.args:
            await update.message.reply_text(
                "ℹ️ **المعلومات العامة**\n\n"
                "اكتب: `معلومات [الموضوع]`\n\n"
                "مثال:\n"
                "`معلومات مصر`\n"
                "`معلومات القمر`\n"
                "`معلومات البيتكوين`",
                parse_mode='Markdown'
            )
            return
        
        topic = ' '.join(context.args).lower()
        
        # قاعدة بيانات بسيطة للمعلومات
        info_db = {
            'مصر': """
🇪🇬 **مصر**

🌍 **القارة:** أفريقيا - آسيا
🏛 **العاصمة:** القاهرة
👥 **السكان:** ~105 مليون
💰 **العملة:** الجنيه المصري (EGP)
📞 **كود الدولة:** +20

🎌 **أشهر المعالم:**
• الأهرامات
• معبد الكرنك
• الأقصر وأسوان
• البحر الأحمر
""",
            'القمر': """
🌙 **القمر**

🌍 **النوع:** قمر طبيعي (تابع للأرض)
📏 **المسافة من الأرض:** 384,400 كم
⏱ **دورة الدوران:** 27.3 يوم
🌡 **درجة الحرارة:** -173°C إلى 127°C

🚀 **أول هبوط:** 1969 (أبولو 11)
👨‍🚀 **أول إنسان:** نيل أرمسترونج
""",
            'فيكتور': """
🤖 **فيكتور**

📅 **الإصدار:** 1.0.0
👑 **المطور:** ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
🏆 **العملة:** فيكتوري (Victory)

💡 **المميزات:**
• إدارة الجروبات
• نظام بنك متكامل
• ألعاب وتسلية
• حماية ذكية

**أفضل بوت في تليجرام!** 🚀
""",
            'البيتكوين': """
₿ **البيتكوين**

📅 **تاريخ الإنشاء:** 2009
👤 **المؤسس:** ساتوشي ناكاموتو (مجهول)
🔢 **الكمية القصوى:** 21 مليون

💰 **السعر الحالي:** ~$65,000 (متغير)
⛏ **طريقة التوليد:** التعدين

⚡ **الخصائص:**
• لامركزي
• غير قابل للتزوير
• شفاف 100%
"""
        }
        
        # البحث في القاعدة
        info = None
        for key, value in info_db.items():
            if key in topic:
                info = value
                break
        
        if not info:
            info = f"""
❓ **معلومات عن: {topic}**

عذراً، مفيش معلومات كافية عن "{topic}" حالياً.

💡 **جرب:** معلومات مصر، معلومات القمر، معلومات فيكتور
"""
        
        await update.message.reply_text(info, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # ⏰ الوقت والتاريخ
    # ═══════════════════════════════════════════════════════
    
    async def cmd_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الوقت"""
        now = datetime.now()
        
        # التاريخ الهجري (تقريبي)
        hijri_months = ['محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني', 'جمادى الأولى', 
                       'جمادى الآخرة', 'رجب', 'شعبان', 'رمضان', 'شوال', 
                       'ذو القعدة', 'ذو الحجة']
        
        # تقريب بسيط (للتوضيح)
        hijri_year = now.year - 579  # تقريب
        hijri_month = hijri_months[now.month - 1]
        hijri_day = now.day
        
        text = f"""
⏰ **الوقت الآن**

📅 **الميلادي:** {now.strftime('%d/%m/%Y')}
🌙 **الهجري:** {hijri_day} {hijri_month} {hijri_year}هـ
⏱ **الوقت:** {now.strftime('%I:%M %p')}

📍 **المنطقة الزمنية:** {SETTINGS['timezone']}
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
