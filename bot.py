import os
import requests
import logging
import re
import threading
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
os.environ['MAIN_BOT_TOKEN'] = '5663514171:AAFo7X3xzuwEYkdQUDFCAc3zzO0L7rzGi5U'
os.environ['REPORT_BOT_TOKEN'] = '5941264407:AAHSEjZJMeRB9DpCQ5D7Ba3O_3MIleJRvkQ'
os.environ['OWNER_CHAT_ID'] = '1626828965'

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
    "ms_black_pipes": {
        "name": "MS Black Pipes",
        "image": "https://goasponge.com/assets/img/product/pp/ms-black-pipes-main.jpg", 
        "description": "Mild Steel Black Pipes for industrial applications",
        "specifications": ["Material: Mild Steel", "Types: ERW, Seamless", "Sizes: 15mm to 150mm"]
    },
    "gp_pipes": {
        "name": "GP Pipes",
        "image": "https://goasponge.com/assets/img/product/pp/gp-pipes-main.jpg",
        "description": "General Purpose Pipes for versatile industrial use", 
        "specifications": ["Material: Mild Steel", "Types: ERW Pipes", "Sizes: 15mm to 150mm"]
    },
    "hot_rolled_semi_coils": {
        "name": "Hot Rolled Semi Coils",
        "image": "https://goasponge.com/assets/img/product/pp/hot-rolled-semi-coils-main.jpg",
        "description": "Hot Rolled Semi Coils for steel manufacturing",
        "specifications": ["Material: Carbon Steel", "Thickness: 1.5mm to 12mm", "Width: 900mm to 1600mm"]
    },
    "ms_billets": {
        "name": "MS Billets",
        "image": "https://goasponge.com/assets/img/product/pp/ms-billets-main.jpg",
        "description": "Mild Steel Billets for rerolling and forging",
        "specifications": ["Material: Mild Steel", "Size: 100x100mm to 150x150mm", "Length: 3-6 meters"]
    },
    "tmt_bars": {
        "name": "TMT Bars", 
        "image": "https://goasponge.com/assets/img/product/pp/tmt-bars-main.jpg",
        "description": "Thermo-Mechanically Treated Bars for construction",
        "specifications": ["Material: Fe-415, Fe-500, Fe-550", "Sizes: 8mm to 32mm", "Standards: IS 1786"]
    },
    "iron_ore_mining": {
        "name": "Iron Ore Mining",
        "image": "https://goasponge.com/assets/img/product/pp/iron-ore-mining-main.jpg", 
        "description": "Sustainable iron ore mining operations",
        "specifications": ["Quality: High-grade Iron Ore", "Fe Content: 58-62%", "Mining Method: Open Cast"]
    },
    "fly_ash_bricks": {
        "name": "Fly Ash Bricks",
        "image": "https://goasponge.com/assets/img/product/pp/flyaash-bricks-main.jpg",
        "description": "Eco-friendly bricks from steel plant byproducts",
        "specifications": ["Compressive Strength: 50-70 kg/cm²", "Water Absorption: 12-15%", "Dimensions: 230x110x75mm"]
    }
}

class GSPLBot:
    def __init__(self):
        self.app = Application.builder().token(MAIN_BOT_TOKEN).build()
        self.setup_handlers()
        logger.info("🤖 GSPL Bot Initialized")

    def setup_handlers(self):
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("status", self.status))
        
        # Callback query handler for buttons
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Message handler for user registration
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Initialize user session
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'name': None, 'email': None, 'mobile': None, 'data_collected': False,
                'current_step': None, 'interaction_count': 0, 'joined_at': datetime.now().isoformat(),
                'telegram_name': user_name, 'telegram_username': update.effective_user.username
            }
        
        await self.show_main_menu(update)

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
        
        welcome_text = """🏭 **Welcome to Goa Sponge & Power Limited**

*24/7 Official Assistant*

📍 **Headquarters:** Goa, India
🏭 **Industry:** Steel & Power
⭐ **Established:** 1999

Choose an option below to explore:"""
        
        if isinstance(update, Update):
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ GSPL Bot is running 24/7 on Render!")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id in user_sessions:
            user_sessions[user_id]['interaction_count'] += 1
        
        callback_data = query.data
        
        if callback_data == "company_info":
            await self.show_company_info(query)
        elif callback_data == "product_catalog":
            await self.show_product_catalog(query)
        elif callback_data == "directors":
            await self.show_directors(query)
        elif callback_data == "financial":
            await self.show_financial_info(query)
        elif callback_data == "media":
            await self.show_media(query)
        elif callback_data == "contact":
            await self.show_contact(query)
        elif callback_data == "register":
            await self.start_registration(query)
        elif callback_data.startswith("product_"):
            product_id = callback_data.replace("product_", "")
            await self.show_product_details(query, product_id)
        elif callback_data == "back_to_main":
            await self.show_main_menu_from_query(query)
        elif callback_data == "back_to_products":
            await self.show_product_catalog(query)

    async def show_company_info(self, query):
        company_text = """🏭 **Goa Sponge & Power Limited**

**About Us:**
Goa Sponge & Power Limited is a leading steel manufacturing company based in Goa, India. We specialize in producing high-quality sponge iron and various steel products.

**Key Highlights:**
• 🏭 Integrated Steel Plant
• 🔥 Sponge Iron Production
• 🏗️ Steel Product Manufacturing
• ⚡ Power Generation
• 🌱 Sustainable Operations

**Vision:**
To be a leading steel manufacturer through innovation, quality, and sustainable practices."""

        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(company_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_product_catalog(self, query):
        keyboard = [
            [InlineKeyboardButton("🟠 Sponge Iron", callback_data="product_sponge_iron")],
            [InlineKeyboardButton("🔵 GI Pipes", callback_data="product_gi_pipes")],
            [InlineKeyboardButton("⚫ MS Black Pipes", callback_data="product_ms_black_pipes")],
            [InlineKeyboardButton("🔶 GP Pipes", callback_data="product_gp_pipes")],
            [InlineKeyboardButton("🌀 Hot Rolled Coils", callback_data="product_hot_rolled_semi_coils")],
            [InlineKeyboardButton("📏 MS Billets", callback_data="product_ms_billets")],
            [InlineKeyboardButton("🏗️ TMT Bars", callback_data="product_tmt_bars")],
            [InlineKeyboardButton("⛏️ Iron Ore Mining", callback_data="product_iron_ore_mining")],
            [InlineKeyboardButton("🧱 Fly Ash Bricks", callback_data="product_fly_ash_bricks")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏗️ **Our Product Catalog**\n\nChoose a product to view details:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_product_details(self, query, product_id):
        if product_id in PRODUCTS_DATA:
            product = PRODUCTS_DATA[product_id]
            
            specs_text = "\n".join([f"• {spec}" for spec in product['specifications']])
            
            product_text = f"""🏗️ **{product['name']}**

{product['description']}

**Specifications:**
{specs_text}

**Quality Standards:** ISO Certified
**Availability:** Ready Stock
**Delivery:** Pan India"""

            keyboard = [
                [InlineKeyboardButton("📞 Enquire Now", callback_data="contact")],
                [InlineKeyboardButton("🔙 Back to Products", callback_data="back_to_products")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(product_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_directors(self, query):
        directors_text = """👥 **Board of Directors**

**Chairman & Managing Director:**
• Mr. S. K. Bhayana

**Whole Time Director:**
• Mr. Vineet Kumar

**Independent Directors:**
• Mr. Arun Kumar Gupta
• Mr. Rajendra Kumar Jalota
• Ms. Renu Jain

**Leadership Team:**
• Experienced professionals
• Industry experts
• Strategic visionaries"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(directors_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_financial_info(self, query):
        financial_text = """📊 **Financial Information**

**Key Financials:**
• Revenue: Growing consistently
• Profitability: Sustainable margins
• Investments: Ongoing expansion

**Stock Information:**
• BSE: 530803
• NSE: GOASPONGE

**Performance:**
• Strong market presence
• Robust financial health
• Strategic investments"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(financial_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_media(self, query):
        media_text = """🎥 **Media & Videos**

**Corporate Videos:**
• Plant Tour
• Manufacturing Process
• Quality Standards

**Photo Gallery:**
• Production Facilities
• Products Portfolio
• Infrastructure

**Latest Updates:**
• Industry News
• Company Announcements
• Market Trends"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(media_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_contact(self, query):
        contact_text = """📞 **Contact Information**

**Head Office:**
Goa Sponge & Power Limited
Goa, India

**Contact Details:**
• 📧 Email: info@goasponge.com
• 📞 Phone: +91-832-1234567
• 🌐 Website: www.goasponge.com

**Business Hours:**
• Monday - Friday: 9:00 AM - 6:00 PM
• Saturday: 9:00 AM - 1:00 PM

**For Product Enquiries:**
Use the registration form for detailed quotes."""

        keyboard = [
            [InlineKeyboardButton("📋 Register for Updates", callback_data="register")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def start_registration(self, query):
        user_id = query.from_user.id
        user_sessions[user_id]['current_step'] = 'name'
        
        await query.edit_message_text(
            "📋 **Registration for Updates**\n\nPlease provide your details to receive updates and product information.\n\nWhat is your full name?",
            parse_mode='Markdown'
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if user_id not in user_sessions:
            await update.message.reply_text("Please use /start to begin.")
            return
        
        current_step = user_sessions[user_id].get('current_step')
        
        if current_step == 'name':
            user_sessions[user_id]['name'] = message_text
            user_sessions[user_id]['current_step'] = 'email'
            await update.message.reply_text("📧 What is your email address?")
            
        elif current_step == 'email':
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message_text):
                user_sessions[user_id]['email'] = message_text
                user_sessions[user_id]['current_step'] = 'mobile'
                await update.message.reply_text("📞 What is your mobile number?")
            else:
                await update.message.reply_text("❌ Please enter a valid email address.")
                
        elif current_step == 'mobile':
            if re.match(r'^[6-9]\d{9}$', message_text):
                user_sessions[user_id]['mobile'] = message_text
                user_sessions[user_id]['data_collected'] = True
                user_sessions[user_id]['current_step'] = None
                
                # Send confirmation
                await update.message.reply_text(
                    f"""✅ **Registration Successful!**

Thank you {user_sessions[user_id]['name']} for registering.

We will contact you at:
• 📧 {user_sessions[user_id]['email']}
• 📞 {user_sessions[user_id]['mobile']}

You will now receive updates about our products and services.""",
                    parse_mode='Markdown'
                )
                
                # Show main menu again
                await self.show_main_menu(update)
                
            else:
                await update.message.reply_text("❌ Please enter a valid 10-digit mobile number.")

    async def show_main_menu_from_query(self, query):
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
        
        welcome_text = """🏭 **Welcome to Goa Sponge & Power Limited**

*24/7 Official Assistant*

Choose an option below to explore:"""
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    def run_bot(self):
        print("🚀 Starting GSPL Bot...")
        logger.info("🤖 GSPL Bot Started Successfully!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = GSPLBot()
    bot.run_bot()
