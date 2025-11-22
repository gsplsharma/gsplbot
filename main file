import os
import requests
import logging
import re
import threading
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configure logging for Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get tokens from Railway environment variables
MAIN_BOT_TOKEN = os.environ.get('MAIN_BOT_TOKEN')
REPORT_BOT_TOKEN = os.environ.get('REPORT_BOT_TOKEN')
OWNER_CHAT_ID = os.environ.get('OWNER_CHAT_ID')

# Store user data
user_sessions = {}

# 🏗️ COMPLETE PRODUCTS DATA
PRODUCTS_DATA = {
    "sponge_iron": {
        "name": "Sponge Iron (DRI)",
        "image": "https://goasponge.com/assets/img/product/pp/sponge-iron-main.jpg",
        "description": "High-quality Direct Reduced Iron for steel manufacturing",
        "specifications": ["Fe Content: 80-90%", "Metallization: 82-88%", "Size: 3-20mm", "Quality: ISO Certified"]
    },
    "gi_pipes": {
        "name": "GI Pipes", 
        "image": "https://goasponge.com/assets/img/product/pp/gi-pipes-main.jpg",
        "description": "Galvanized Iron Pipes for corrosion-resistant applications",
        "specifications": ["Material: Galvanized Iron", "Sizes: 15mm to 150mm", "Standards: IS 1239, IS 3589"]
    },
    # ... (sare products yahi rahenge - full code jaise aapke paas hai)
}

class GSPLRailwayBot:
    def __init__(self):
        self.main_app = Application.builder().token(MAIN_BOT_TOKEN).build()
        self.report_app = Application.builder().token(REPORT_BOT_TOKEN).build()
        self.setup_handlers()
        logger.info("🤖 GSPL Bot Initialized for Railway")
    
    def setup_handlers(self):
        # Main Bot Handlers
        self.main_app.add_handler(CommandHandler("start", self.main_start))
        self.main_app.add_handler(CommandHandler("status", self.status))
        self.main_app.add_handler(CallbackQueryHandler(self.main_button_handler))
        self.main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.main_message_handler))
        
        # Report Bot Handlers
        self.report_app.add_handler(CommandHandler("start", self.report_start))
        self.report_app.add_handler(CommandHandler("users", self.show_users_secure))
        self.report_app.add_handler(CommandHandler("myid", self.get_my_id_secure))

    # Status command for monitoring
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ GSPL Bot is running 24/7 on Railway!")

    # 🔒 SECURE REPORT BOT
    async def get_my_id_secure(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.chat.id) != OWNER_CHAT_ID:
            await update.message.reply_text("❌ Access Denied")
            return
        chat_id = update.message.chat.id
        await update.message.reply_text(f"🆔 Your Chat ID: `{chat_id}`", parse_mode='Markdown')

    async def report_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.chat.id) != OWNER_CHAT_ID:
            await update.message.reply_text("❌ Access Denied")
            return
        await update.message.reply_text("🔒 Secure Report Bot - Use /users or /myid")

    async def show_users_secure(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.chat.id) != OWNER_CHAT_ID:
            await update.message.reply_text("❌ Access Denied")
            return
        if not user_sessions:
            await update.message.reply_text("❌ No users registered yet.")
            return
        
        user_list = "🔒 Registered Users:\n\n"
        for user_id, data in user_sessions.items():
            if data.get('data_collected'):
                user_list += f"👤 Name: {data.get('name', 'N/A')}\n"
                user_list += f"📞 Mobile: {data.get('mobile', 'N/A')}\n"
                user_list += f"📧 Email: {data.get('email', 'N/A')}\n"
                user_list += f"🆔 TG ID: {user_id}\n"
                user_list += "─" * 20 + "\n"
        
        await update.message.reply_text(user_list)

    # 🏭 MAIN BOT FUNCTIONS
    async def main_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'name': None, 'email': None, 'mobile': None, 'data_collected': False,
                'current_step': None, 'interaction_count': 0, 'joined_at': datetime.now().isoformat(),
                'telegram_name': user_name, 'telegram_username': update.effective_user.username
            }
        
        await self.show_main_menu(update)
        await self.send_user_report(user_id, user_name, "started")

    async def show_main_menu(self, update):
        keyboard = [
            [InlineKeyboardButton("🏭 Company Overview", callback_data="company_info")],
            [InlineKeyboardButton("🏗️ Products (9)", callback_data="product_catalog")],
            [InlineKeyboardButton("👥 Board of Directors", callback_data="directors")],
            [InlineKeyboardButton("📊 Financial Info", callback_data="financial")],
            [InlineKeyboardButton("🎥 Media & Videos", callback_data="media")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact")],
            [InlineKeyboardButton("📋 Register for Updates", callback_data="register")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = "🏭 **Welcome to Goa Sponge & Power Limited**\n\n*24/7 Official Assistant*"
        
        if isinstance(update, Update):
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    # ... (baaki ke functions aapke original code ke hisaab se)

    # 🚀 RAILWAY 24/7 RUNNER
    def run_on_railway(self):
        """Run both bots on Railway"""
        print("🚀 Starting GSPL Bot on Railway...")
        logger.info("Starting bots on Railway")
        
        def run_main_bot():
            logger.info("🏭 Main Bot Starting...")
            try:
                self.main_app.run_polling()
            except Exception as e:
                logger.error(f"Main bot error: {e}")
                time.sleep(10)
                run_main_bot()
                
        def run_report_bot():
            logger.info("🔒 Report Bot Starting...")
            try:
                self.report_app.run_polling()
            except Exception as e:
                logger.error(f"Report bot error: {e}")
                time.sleep(10)
                run_report_bot()
        
        # Run in separate threads
        main_thread = threading.Thread(target=run_main_bot, daemon=True)
        report_thread = threading.Thread(target=run_report_bot, daemon=True)
        
        main_thread.start()
        report_thread.start()
        
        print("✅ GSPL Bot Successfully Deployed on Railway!")
        print("🏭 Main Bot: Running")
        print("🔒 Report Bot: Running") 
        print("🌐 24/7 Service: ACTIVE")
        
        # Keep alive
        try:
            while True:
                time.sleep(60)
                logger.info("🤖 Bot heartbeat - Running on Railway")
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")

if __name__ == "__main__":
    bot = GSPLRailwayBot()
    bot.run_on_railway()
