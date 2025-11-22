import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Environment variables
os.environ['MAIN_BOT_TOKEN'] = '5663514171:AAFo7X3xzuwEYkdQUDFCAc3zzO0L7rzGi5U'
os.environ['REPORT_BOT_TOKEN'] = '5941264407:AAHSEjZJMeRB9DpCQ5D7Ba3O_3MIleJRvkQ'
os.environ['OWNER_CHAT_ID'] = '1626828965'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_BOT_TOKEN = os.environ.get('MAIN_BOT_TOKEN')

class GSPLBot:
    def __init__(self):
        self.app = Application.builder().token(MAIN_BOT_TOKEN).build()
        self.setup_handlers()
        logger.info("🤖 GSPL Bot Initialized")

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🏭 Company Overview", callback_data="company")],
            [InlineKeyboardButton("🏗️ Products", callback_data="products")],
            [InlineKeyboardButton("📞 Contact", callback_data="contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🏭 **Welcome to Goa Sponge & Power Limited**\n\n*24/7 Official Assistant*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ GSPL Bot is running 24/7 on Render!")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "company":
            await query.edit_message_text("🏭 **Goa Sponge & Power Limited**\n\nLeading steel manufacturing company...")
        elif query.data == "products":
            await query.edit_message_text("🏗️ **Our Products:**\n• Sponge Iron\n• GI Pipes\n• TMT Bars\n• MS Billets")
        elif query.data == "contact":
            await query.edit_message_text("📞 **Contact Support:**\nEmail: info@goasponge.com\nPhone: +91-832-1234567")

    def run(self):
        logger.info("🚀 Starting GSPL Bot...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = GSPLBot()
    bot.run()
