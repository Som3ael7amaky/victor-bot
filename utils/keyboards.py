"""
فيكتور - الأزرار المشتركة
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    """مكتبة الأزرار الجاهزة"""
    
    # ═══════════════════════════════════════════════════════
    # 🏠 القائمة الرئيسية
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def main_menu():
        """القائمة الرئيسية"""
        keyboard = [
            [
                InlineKeyboardButton("🏦 البنك", callback_data='menu_bank'),
                InlineKeyboardButton("🛒 المتجر", callback_data='menu_shop')
            ],
            [
                InlineKeyboardButton("🎮 العب", callback_data='menu_play'),
                InlineKeyboardButton("🛠 الأدوات", callback_data='menu_tools')
            ],
            [
                InlineKeyboardButton("📊 حالتي", callback_data='menu_status'),
                InlineKeyboardButton("❓ المساعدة", callback_data='menu_help')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🏦 أزرار البنك
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def bank_menu():
        """قائمة البنك"""
        keyboard = [
            [
                InlineKeyboardButton("📥 إيداع", callback_data='bank_deposit'),
                InlineKeyboardButton("📤 سحب", callback_data='bank_withdraw')
            ],
            [
                InlineKeyboardButton("🏦 تغيير البنك", callback_data='bank_change'),
                InlineKeyboardButton("📈 الفايدة", callback_data='bank_interest')
            ],
            [
                InlineKeyboardButton("💸 تحويل", callback_data='bank_transfer'),
                InlineKeyboardButton("🔙 رجوع", callback_data='back_main')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def bank_selection():
        """اختيار البنك"""
        keyboard = [
            [InlineKeyboardButton("🔵 بنك فيكتور (آمن)", callback_data='select_bank_victor')],
            [InlineKeyboardButton("🔴 بنك المخاطرة (جريء)", callback_data='select_bank_risk')],
            [InlineKeyboardButton("🟢 بنك المستقبل (تقني)", callback_data='select_bank_future')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='bank_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🛒 أزرار المتجر
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def shop_categories():
        """أقسام المتجر"""
        keyboard = [
            [InlineKeyboardButton("🔧 الأدوات", callback_data='shop_tools')],
            [InlineKeyboardButton("🏠 العقارات", callback_data='shop_properties')],
            [InlineKeyboardButton("🏢 الشركات", callback_data='shop_companies')],
            [InlineKeyboardButton("🛡️ التأمين", callback_data='shop_insurance')],
            [InlineKeyboardButton("💎 الترف", callback_data='shop_luxury')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def shop_item_actions(item_id: str, price: int):
        """أزرار شراء سلعة"""
        keyboard = [
            [
                InlineKeyboardButton(f"🛒 شرى بـ {price:,}", callback_data=f'buy_{item_id}'),
                InlineKeyboardButton("❌ إلغاء", callback_data='shop_cancel')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 💼 أزرار الوظائف
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def jobs_list(jobs: list):
        """قائمة الوظائف"""
        keyboard = []
        for job in jobs[:5]:  # أول 5 وظائف
            keyboard.append([
                InlineKeyboardButton(
                    f"{job['name']} ({job['salary']:,})",
                    callback_data=f'job_apply_{job["id"]}'
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_main')])
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🎮 أزرار الألعاب
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def games_menu():
        """قائمة الألعاب"""
        keyboard = [
            [InlineKeyboardButton("⭕ إكس أوه", callback_data='game_xo')],
            [InlineKeyboardButton("✊ حجر ورقة مقص", callback_data='game_rps')],
            [InlineKeyboardButton("🎯 تحدي", callback_data='game_challenge')],
            [InlineKeyboardButton("😂 نكتة", callback_data='game_joke')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def xo_board(board: list, game_id: str):
        """لوحة إكس أوه"""
        keyboard = []
        symbols = {0: '·', 'X': '❌', 'O': '⭕'}
        
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                pos = i + j
                cell = board[pos] if board[pos] != ' ' else '·'
                row.append(InlineKeyboardButton(
                    cell,
                    callback_data=f'xo_move_{game_id}_{pos}'
                ))
            keyboard.append(row)
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rps_choices(user_id: int):
        """اختيارات حجر ورقة مقص"""
        keyboard = [
            [
                InlineKeyboardButton("✊ حجر", callback_data=f'rps_rock_{user_id}'),
                InlineKeyboardButton("📄 ورقة", callback_data=f'rps_paper_{user_id}'),
                InlineKeyboardButton("✂️ مقص", callback_data=f'rps_scissors_{user_id}')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🛠 أزرار الأدوات
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def tools_menu():
        """قائمة الأدوات"""
        keyboard = [
            [
                InlineKeyboardButton("🌤 الطقس", callback_data='tool_weather'),
                InlineKeyboardButton("🌐 ترجمة", callback_data='tool_translate')
            ],
            [
                InlineKeyboardButton("🧮 حاسبة", callback_data='tool_calc'),
                InlineKeyboardButton("💱 عملات", callback_data='tool_currency')
            ],
            [
                InlineKeyboardButton("ℹ️ معلومات", callback_data='tool_info'),
                InlineKeyboardButton("⏰ وقت", callback_data='tool_time')
            ],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # ⚙️ أزرار الإعدادات
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def settings_menu(is_admin: bool = False):
        """قائمة الإعدادات"""
        keyboard = [
            [InlineKeyboardButton("🎭 تغيير اسم البوت", callback_data='set_nickname')],
            [InlineKeyboardButton("👋 إعدادات الترحيب", callback_data='set_welcome')],
            [InlineKeyboardButton("🛡️ إعدادات الحماية", callback_data='set_protection')]
        ]
        
        if is_admin:
            keyboard.append([InlineKeyboardButton("🔒 الوضع الهادئ", callback_data='set_silent')])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_main')])
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 👑 أزرار المطور
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def developer_menu():
        """قائمة المطور"""
        keyboard = [
            [InlineKeyboardButton("📊 إحصائيات", callback_data='dev_stats')],
            [InlineKeyboardButton("📢 بث عام", callback_data='dev_broadcast')],
            [InlineKeyboardButton("💰 إعطاء فلوس", callback_data='dev_give')],
            [InlineKeyboardButton("🚫 حظر عام", callback_data='dev_ban')],
            [InlineKeyboardButton("⚙️ إعدادات", callback_data='dev_settings')],
            [InlineKeyboardButton("📋 سجلات", callback_data='dev_logs')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str):
        """تأكيد إجراء"""
        keyboard = [
            [
                InlineKeyboardButton("✅ نعم", callback_data=f'confirm_{action}'),
                InlineKeyboardButton("❌ لا", callback_data='cancel_action')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🔙 أزرار التنقل
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def back_button(destination: str = 'main'):
        """زر رجوع فقط"""
        keyboard = [[
            InlineKeyboardButton("🔙 رجوع", callback_data=f'back_{destination}')
        ]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def close_button():
        """زر إغلاق"""
        keyboard = [[
            InlineKeyboardButton("❌ إغلاق", callback_data='close_message')
        ]]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 📱 أزرار الترحيب
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def welcome_actions(user_id: int):
        """أزرار الترحيب"""
        keyboard = [
            [
                InlineKeyboardButton("🏦 البنك", callback_data=f'welcome_bank_{user_id}'),
                InlineKeyboardButton("📋 الأوامر", callback_data=f'welcome_cmds_{user_id}')
            ],
            [
                InlineKeyboardButton("⚖️ القوانين", callback_data=f'welcome_rules_{user_id}'),
                InlineKeyboardButton("🎮 العب", callback_data=f'welcome_play_{user_id}')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 💍 أزرار الزواج
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def marriage_actions(partner_id: int, dowry: int):
        """أزرار الزواج"""
        keyboard = [
            [
                InlineKeyboardButton(f"💍 أوافق (المهر {dowry:,})", 
                                   callback_data=f'marry_accept_{partner_id}_{dowry}'),
                InlineKeyboardButton("❌ أرفض", callback_data=f'marry_reject_{partner_id}')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🎁 أزرار الكنوز
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def treasure_hunt(can_hunt: bool = True):
        """زر البحث عن كنز"""
        if can_hunt:
            keyboard = [[
                InlineKeyboardButton("🔍 ابحث عن كنز!", callback_data='treasure_hunt')
            ]]
        else:
            keyboard = [[
                InlineKeyboardButton("⏳ انتظر غداً", callback_data='treasure_wait')
            ]]
        return InlineKeyboardMarkup(keyboard)
    
    # ═══════════════════════════════════════════════════════
    # 🏆 أزرار التوبات
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def leaderboard_categories():
        """اختيار نوع التوب"""
        keyboard = [
            [InlineKeyboardButton("💰 الأغنياء", callback_data='top_rich')],
            [InlineKeyboardButton("🏆 الأكثر نشاطاً", callback_data='top_active')],
            [InlineKeyboardButton("💍 أقوى زواج", callback_data='top_marriage')],
            [InlineKeyboardButton("🎮 ألعاب", callback_data='top_games')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
