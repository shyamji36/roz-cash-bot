import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask server to satisfy Render port binding requirement
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Telegram Bot Token
BOT_TOKEN = "9126975810:AAHD34l3tnFgh6pmCS8zgf203kqkGb-s_cY"

# In-memory database for users and balances (aap baad mein isme database jod sakte hain)
users_db = {}

# Main Menu Keyboard
def get_main_keyboard():
    keyboard = [
        ["💰 Balance", "👥 Refer & Earn"],
        ["💸 Withdraw", "🎁 Daily Bonus"],
        ["ℹ️ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Register user if new
    if user_id not in users_db:
        users_db[user_id] = {
            "name": user.first_name,
            "balance": 5.0,  # Joining bonus
            "referrals": 0
        }

    welcome_text = (
        f"👋 Namaste {user.first_name} ji!\n\n"
        f"Welcome to Roz Cash Bot. Aap yahan dosto ko refer karke aur daily rewards ke zariye paise kama sakte hain.\n"
        f"🎁 Aapko  ₹5.0 Joining Bonus mil gaya hai!\n\n"
        f"Neeche diye gaye buttons ka istemaal karein:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # Ensure user exists in db
    if user_id not in users_db:
        users_db[user_id] = {"name": update.effective_user.first_name, "balance": 0.0, "referrals": 0}

    user_data = users_db[user_id]

    if text == "💰 Balance":
        balance = user_data["balance"]
        referrals = user_data["referrals"]
        await update.message.reply_text(
            f"👤 **Account Details:**\n\n"
            f"💵 Current Balance: ₹{balance}\n"
            f"👥 Total Referrals: {referrals}\n\n"
            f"Kamanay ke liye dosto ko refer karein!",
            reply_markup=get_main_keyboard()
        )

    elif text == "👥 Refer & Earn":
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        await update.message.reply_text(
            f"🔗 **Refer & Earn Program**\n\n"
            f"Apne dost ko is link se invite karein aur har referral par ₹2 paayein!\n\n"
            f"Aapka Referral Link:\n`{ref_link}`",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    elif text == "💸 Withdraw":
        balance = user_data["balance"]
        min_withdraw = 50.0
        if balance >= min_withdraw:
            await update.message.reply_text(
                f"✅ Aapka balance ₹{balance} hai. Withdrawal request process ki ja rahi hai. Kripya apna UPI ID bhejein.",
                reply_markup=get_main_keyboard()
            )
        else:
            needed = min_withdraw - balance
            await update.message.reply_text(
                f"❌ Minimum withdrawal limit ₹{min_withdraw} hai.\n"
                f"Aapko ₹{needed} aur chahiye withdraw karne ke liye. Dosto ko refer karein!",
                reply_markup=get_main_keyboard()
            )

    elif text == "🎁 Daily Bonus":
        await update.message.reply_text(
            "🎁 Aapko aaj ka Daily Bonus ₹1 mil gaya hai!",
            reply_markup=get_main_keyboard()
        )
        user_data["balance"] += 1.0

    elif text == "ℹ️ Help":
        await update.message.reply_text(
            "ℹ️ **Help & Support**\n\n"
            "1. Dosto ko refer karke paise kamayein.\n"
            "2. Daily bonus claim karein.\n"
            "3. Minimum ₹50 hone par UPI ya Bank mein withdraw karein.\n\n"
            "Kisi bhi samasya ke liye admin se sampark karein.",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "Kripya niche diye gaye menu buttons ka istemaal karein.",
            reply_markup=get_main_keyboard()
        )

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is starting with full features...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
