"""
فيكتور - معالج التسلية
المطور: ًِ𝙎ُِ𝙊ِّّ𝙈3َٰ𝘼ٱلْـﺳ〄لـطٱﻧـ⸙
"""

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import DEVELOPER, CURRENCY, is_developer

class FunHandler:
    """معالج التسلية والألعاب"""
    
    def __init__(self):
        self.active_games = {}
        self.jokes = self.load_jokes()
        self.challenges = self.load_challenges()
    
    # ═══════════════════════════════════════════════════════
    # 😂 النكت
    # ═══════════════════════════════════════════════════════
    
    async def cmd_joke(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إرسال نكتة"""
        user = update.effective_user
        joke = random.choice(self.jokes)
        
        if is_developer(user.id):
            joke += "\n\n👑 *نكتة خاصة للمطور الإلهي*"
        
        await update.message.reply_text(joke, parse_mode='Markdown')
    
    def load_jokes(self):
        """تحميل النكت"""
        return [
            """
😂 **نكتة اليوم**

واحد راح للدكتور قاله:
- يا دكتور أنا بحلم إني أكون طيارة!
قاله الدكتور:
- خد هذي البنادول!
قاله:
- بنادول إزاي؟ أنا طيارة!
قاله الدكتور:
- عشان ما تزعجش حد بالليل 😂
""",
            """
😂 **نكتة**

مرة واحد اشترى مكيف جديد...
قعد يضرب فيه ضرب!
قالوله ليه؟
قال: الكهربا قالت "اضرب مكيف" 😂
""",
            """
😂 **نكتة فيكتور**

مرة فيكتور قال لمستخدم:
- أنا بوت ذكي!
قاله المستخدم:
- طب قولي نكتة!
قال فيكتور:
- أنا بوت ذكي... بس مش كفاية عشان أقول نكتة حلوة! 😂
"""
        ]
    
    # ═══════════════════════════════════════════════════════
    # 🎮 الألعاب
    # ═══════════════════════════════════════════════════════
    
    async def cmd_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء لعبة"""
        user = update.effective_user
        
        if not context.args:
            keyboard = [
                [InlineKeyboardButton("⭕ إكس أوه (XO)", callback_data=f'game_xo_{user.id}')],
                [InlineKeyboardButton("✊ حجر ورقة مقص", callback_data=f'game_rps_{user.id}')]
            ]
            
            await update.message.reply_text(
                "🎮 **اختار لعبتك:**",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            return
        
        game_type = context.args[0].lower()
        
        if game_type in ['xo', 'اكس', 'اكس او']:
            await self.start_xo(update, context)
        elif game_type in ['حجر', 'rps', 'حجرة']:
            await self.start_rps(update, context)
        else:
            await update.message.reply_text("🎮 اكتب 'لعبة' عشان تشوف القائمة")
    
    async def start_xo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء لعبة XO"""
        user = update.effective_user
        
        if update.message.reply_to_message:
            opponent = update.message.reply_to_message.from_user
            
            if opponent.id == user.id:
                await update.message.reply_text("🤔 مش هتلعب مع نفسك صح؟")
                return
            
            if opponent.is_bot and not is_developer(user.id):
                await update.message.reply_text("🤖 مينفعش تلعب مع البوت (إلا المطور)")
                return
            
            game_id = f"{user.id}_{opponent.id}"
            self.active_games[game_id] = {
                'type': 'xo',
                'player1': user.id,
                'player2': opponent.id,
                'board': [' ' for _ in range(9)],
                'current': user.id,
                'names': {user.id: user.first_name, opponent.id: opponent.first_name}
            }
            
            await self.send_xo_board(update, context, game_id)
        else:
            game_id = f"{user.id}_bot"
            self.active_games[game_id] = {
                'type': 'xo',
                'player1': user.id,
                'player2': 'bot',
                'board': [' ' for _ in range(9)],
                'current': user.id,
                'names': {user.id: user.first_name, 'bot': 'فيكتور 🤖'}
            }
            
            await self.send_xo_board(update, context, game_id)
    
    async def send_xo_board(self, update, context, game_id):
        """إرسال لوحة XO"""
        game = self.active_games.get(game_id)
        if not game:
            return
        
        board = game['board']
        current_name = game['names'].get(game['current'], 'اللاعب')
        
        text = f"""
⭕ **لعبة إكس أوه** ❌

{current_name} دورك!

      {board[0]} │ {board[1]} │ {board[2]}
───┼───┼───
{board[3]} │ {board[4]} │ {board[5]}
───┼───┼───
{board[6]} │ {board[7]} │ {board[8]}
      """
        
        keyboard = []
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                pos = i + j
                symbol = board[pos] if board[pos] != ' ' else '·'
                row.append(InlineKeyboardButton(symbol, callback_data=f'xo_move_{game_id}_{pos}'))
            keyboard.append(row)
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def start_rps(self, update, context):
        """بدء لعبة حجر ورقة مقص"""
        user = update.effective_user
        
        keyboard = [
            [
                InlineKeyboardButton("✊ حجر", callback_data=f'rps_rock_{user.id}'),
                InlineKeyboardButton("📄 ورقة", callback_data=f'rps_paper_{user.id}'),
                InlineKeyboardButton("✂️ مقص", callback_data=f'rps_scissors_{user.id}')
            ]
        ]
        
        await update.message.reply_text(
            "✊ **حجر ورقة مقص**\n\nاختار:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════════
    # 👊 التفاعلات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_slap(self, update, context):
        """صفع"""
        await self.send_interaction(update, context, "صفع", "👋")
    
    async def cmd_hug(self, update, context):
        """حضن"""
        await self.send_interaction(update, context, "حضن", "🤗")
    
    async def send_interaction(self, update, context, action, emoji):
        """إرسال تفاعل"""
        message = update.effective_message
        user = update.effective_user
        
        if not message.reply_to_message:
            await message.reply_text(f"🤔 رد على رسالة الشخص اللي عايز ت{action}ه!")
            return
        
        target = message.reply_to_message.from_user
        
        if is_developer(target.id) and action in ['صفع', 'ركل']:
            await message.reply_text(
                f"⛔ **مينفعش ت{action} المطور الإلهي!**\n\nهو اللي هي{action}ك دلوقتي! 😂",
                parse_mode='Markdown'
            )
            return
        
        text = f"{emoji} **{user.first_name}** {action} **{target.first_name}**! {emoji * 3}"
        await message.reply_text(text, parse_mode='Markdown')
    
    # ═══════════════════════════════════════════════════════
    # 🎯 التحديات
    # ═══════════════════════════════════════════════════════
    
    async def cmd_challenge(self, update, context):
        """إرسال تحدي"""
        user = update.effective_user
        challenge = random.choice(self.challenges)
        
        text = f"""
🎯 **تحدي جديد!**

{challenge['text']}

⏱️ **الوقت:** {challenge['time']} ثانية
🏆 **الجائزة:** {challenge['reward']:,} {CURRENCY['symbol']}

مين هيعملها؟ 😎
"""
        
        keyboard = [[InlineKeyboardButton("💪 أنا!", callback_data=f'challenge_accept_{user.id}')]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    def load_challenges(self):
        """تحميل التحديات"""
        return [
            {'text': 'اكتب اسمك بالعكس في 10 ثواني!', 'time': 10, 'reward': 500},
            {'text': 'عد من 1 لـ 20 بدون غلطة!', 'time': 15, 'reward': 300},
            {'text': 'قول 5 أسماء بحرف الألف!', 'time': 20, 'reward': 400},
            {'text': 'اكتب "فيكتور هو الأفضل" 3 مرات!', 'time': 12, 'reward': 600}
        ]
    
    # ═══════════════════════════════════════════════════════
    # 🔘 معالج الأزرار
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, update, context):
        """معالج أزرار الألعاب"""
        query = update.callback_query
        data = query.data
        
        if data.startswith('game_'):
            game_type = data.split('_')[1]
            if game_type == 'xo':
                await query.answer("⭕ اكتب: لعبة xo")
            elif game_type == 'rps':
                await query.answer("✊ اكتب: لعبة حجر")
        
        elif data.startswith('xo_move_'):
            parts = data.split('_')
            game_id = f"{parts[2]}_{parts[3]}"
            position = int(parts[4])
            await self.handle_xo_move(update, context, game_id, position)
        
        elif data.startswith('rps_'):
            choice = data.split('_')[1]
            user_id = int(data.split('_')[2])
            await self.handle_rps_choice(update, context, choice, user_id)
        
        elif data.startswith('challenge_accept_'):
            await query.answer("💪 تحدى نفسك واعملها!")
            await query.edit_message_text(
                query.message.text + "\n\n💪 **تم القبول!** حظ موفق!",
                parse_mode='Markdown'
            )
    
    async def handle_xo_move(self, update, context, game_id, position):
        """معالجة حركة XO"""
        query = update.callback_query
        game = self.active_games.get(game_id)
        
        if not game:
            await query.answer("❌ اللعبة انتهت!")
            return
        
        if query.from_user.id != game['current']:
            await query.answer("⏳ مش دورك!")
            return
        
        if game['board'][position] != ' ':
            await query.answer("❌ المكان مش فاضي!")
            return
        
        symbol = '❌' if game['current'] == game['player1'] else '⭕'
        game['board'][position] = symbol
        
        winner = self.check_xo_winner(game['board'])
        if winner:
            await self.end_xo_game(update, context, game_id, winner)
            return
        
        if ' ' not in game['board']:
            await self.end_xo_game(update, context, game_id, 'draw')
            return
        
        game['current'] = game['player2'] if game['current'] == game['player1'] else game['player1']
        
        if game['current'] == 'bot':
            await self.bot_xo_move(update, context, game_id)
        else:
            await self.update_xo_board(update, context, game_id)
        
        await query.answer()
    
    def check_xo_winner(self, board):
        """التحقق من الفائز"""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in lines:
            if board[line[0]] == board[line[1]] == board[line[2]] != ' ':
                return board[line[0]]
        return None
    
    async def bot_xo_move(self, update, context, game_id):
        """حركة البوت"""
        game = self.active_games[game_id]
        empty = [i for i, x in enumerate(game['board']) if x == ' ']
        
        if empty:
            move = self.find_best_move(game['board']) or random.choice(empty)
            game['board'][move] = '⭕'
            
            winner = self.check_xo_winner(game['board'])
            if winner:
                await self.end_xo_game(update, context, game_id, winner)
                return
            
            if ' ' not in game['board']:
                await self.end_xo_game(update, context, game_id, 'draw')
                return
            
            game['current'] = game['player1']
            await self.update_xo_board(update, context, game_id)
    
    def find_best_move(self, board):
        """إيجاد أفضل حركة"""
        for i in range(9):
            if board[i] == ' ':
                board[i] = '⭕'
                if self.check_xo_winner(board):
                    board[i] = ' '
                    return i
                board[i] = ' '
        
        for i in range(9):
            if board[i] == ' ':
                board[i] = '❌'
                if self.check_xo_winner(board):
                    board[i] = ' '
                    return i
                board[i] = ' '
        
        if board[4] == ' ':
            return 4
        return None
    
    async def update_xo_board(self, update, context, game_id):
        """تحديث لوحة XO"""
        game = self.active_games[game_id]
        board = game['board']
        current_name = game['names'].get(game['current'], 'اللاعب')
        
        text = f"""
⭕ **لعبة إكس أوه** ❌

{current_name} دورك!

      {board[0]} │ {board[1]} │ {board[2]}
───┼───┼───
{board[3]} │ {board[4]} │ {board[5]}
───┼───┼───
{board[6]} │ {board[7]} │ {board[8]}
      """
        
        keyboard = []
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                pos = i + j
                symbol = board[pos] if board[pos] != ' ' else '·'
                row.append(InlineKeyboardButton(symbol, callback_data=f'xo_move_{game_id}_{pos}'))
            keyboard.append(row)
        
        try:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except:
            pass
    
    async def end_xo_game(self, update, context, game_id, result):
        """إنهاء لعبة XO"""
        game = self.active_games.pop(game_id, None)
        if not game:
            return
        
        if result == 'draw':
            text = "🤝 **تعادل!**"
        else:
            winner_name = game['names'].get(game['player1'] if result == '❌' else game['player2'], 'الفائز')
            text = f"🎉 **{winner_name} فاز!**"
        
        try:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown')
        except:
            pass
    
    async def handle_rps_choice(self, update, context, choice, user_id):
        """معالجة اختيار حجر ورقة مقص"""
        query = update.callback_query
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        
        names = {'rock': '✊ حجر', 'paper': '📄 ورقة', 'scissors': '✂️ مقص'}
        
        if choice == bot_choice:
            result = "🤝 **تعادل!**"
        elif ((choice == 'rock' and bot_choice == 'scissors') or
              (choice == 'paper' and bot_choice == 'rock') or
              (choice == 'scissors' and bot_choice == 'paper')):
            result = "🎉 **فزت!**"
        else:
            result = "😅 **فيكتور فاز!**"
        
        text = f"""
✊ **حجر ورقة مقص**

أنت: {names[choice]}
فيكتور: {names[bot_choice]}

{result}
"""
        
        await query.edit_message_text(text, parse_mode='Markdown')
