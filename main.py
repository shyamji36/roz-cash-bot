import os
import time
from datetime import date
import logging
from flask import Flask
from threading import Thread
import telebot
from telebot import types

# Flask server setup to satisfy Render port binding requirement
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Telegram Bot Setup
TOKEN = '9126975810:AAFthAtAMIcT5_giUKAnNnIUuI2_TrDh74k'
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user data
users = {}

# Track user states (for setting UPI or Bank details)
user_states = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_balance = types.KeyboardButton("💰 My Balance")
    btn_ref = types.KeyboardButton("🚀 Refer & Earn")
    btn_withdraw = types.KeyboardButton("💸 Withdraw Money")
    btn_bonus = types.KeyboardButton("🎁 Daily Bonus")
    btn_account = types.KeyboardButton("⚙️ Account & UPI")
    markup.add(btn_balance, btn_ref)
    markup.add(btn_withdraw, btn_bonus)
    markup.add(btn_account)
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if user_id not in users:
        users[user_id] = {
            "balance": 5,           # Joining Bonus ₹5
            "referred_by": None,
            "referral_count": 0,    # Total referrals count
            "last_bonus_date": None,
            "payout_method": "Not Set",
            "payout_details": "Not Set"
        }
        
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if referrer_id in users and referrer_id != user_id:
                    users[user_id]["referred_by"] = referrer_id
                    users[referrer_id]["balance"] += 3            # Referrer gets ₹3 bonus
                    users[referrer_id]["referral_count"] += 1     # Total count +1
                    
                    bot.send_message(
                        referrer_id, 
                        "🔥 ── **NEW REFERRAL JOINED!** ── 🔥\n\n"
                        "🎉 A new user joined using your referral link!\n"
                        "💰 **+₹3** has been successfully added to your account. 🚀",
                        parse_mode="Markdown"
                    )
            except ValueError:
                pass

    bot_username = bot.get_me().username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    current_balance = users[user_id]["balance"]
    
    welcome_msg = (
        f"╔═════════════════════╗\n"
        f"      🌟 **ROZ CASH BOT** 🌟      \n"
        f"╚═════════════════════╝\n\n"
        f"👋 Hello friend! Welcome to the bot.\n\n"
        f"🎁 **Joining Bonus:** `₹5 Free`\n"
        f"💎 **Your Balance:** `₹{current_balance}`\n\n"
        f"🔗 **Your Referral Link:**\n"
        f"`{ref_link}`\n\n"
        f"⚡ *Share with friends & earn ₹3 per join!*\n"
        f"👇 *Choose an option from the menu below:*"
    )
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    if user_id not in users:
        users[user_id] = {
            "balance": 5, 
            "referred_by": None, 
            "referral_count": 0, 
            "last_bonus_date": None,
            "payout_method": "Not Set",
            "payout_details": "Not Set"
        }
    
    state = user_states.get(user_id)
    if state == "waiting_for_upi":
        users[user_id]["payout_method"] = "UPI"
        users[user_id]["payout_details"] = text
        user_states[user_id] = None
        bot.reply_to(message, f"✅ **UPI ID Saved Successfully!**\n`{text}`", parse_mode="Markdown", reply_markup=get_main_keyboard())
        return
        
    elif state == "waiting_for_bank":
        users[user_id]["payout_method"] = "Bank Account"
        users[user_id]["payout_details"] = text
        user_states[user_id] = None
        bot.reply_to(message, f"✅ **Bank Details Saved Successfully!**\n`{text}`", parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

    if text == "💰 My Balance":
        balance = users[user_id]["balance"]
        ref_count = users[user_id]["referral_count"]
        method = users[user_id]["payout_method"]
        details = users[user_id]["payout_details"]
        bal_msg = (
            f"┌──────── 👝 **WALLET** ────────┐\n\n"
            f"   💰 Available Balance: **₹{balance}**\n"
            f"   👥 Total Referrals: **{ref_count} Users**\n"
            f"   💳 Payout Mode: `{method}`\n"
            f"   📄 Details: `{details}`\n"
            f"   🟢 Account Status: **Active**\n\n"
            f"└──────────────────────────┘"
        )
        bot.reply_to(message, bal_msg, parse_mode="Markdown")
        
    elif text == "🚀 Refer & Earn":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        ref_count = users[user_id]["referral_count"]
        ref_msg = (
            f"┌────── 🚀 **REFER & EARN** ──────┐\n\n"
            f"🔗 **Your Link:**\n`{ref_link}`\n\n"
            f"👥 **Total Joins:** `{ref_count} Friends`\n"
            f"💡 *Earn **₹3** for every successful invite!*\n"
            f"Share it on WhatsApp & Telegram! 💸\n\n"
            f"└──────────────────────────┘"
        )
        bot.reply_to(message, ref_msg, parse_mode="Markdown")
        
    elif text == "💸 Withdraw Money":
        balance = users[user_id]["balance"]
        if balance < 100:
            wd_msg = (
                f"┌───── 💸 **WITHDRAWAL** ─────┐\n\n"
                f"⚠️ **Minimum Payout:** ₹100\n"
                f"❌ Your balance is currently below the limit (`₹{balance}`).\n\n"
                f"🏃‍♂️ Refer more friends to reach ₹100 quickly!\n\n"
                f"└──────────────────────────┘"
            )
            bot.reply_to(message, wd_msg, parse_mode="Markdown")
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📱 UPI ID", callback_data="withdraw_upi"),
                types.InlineKeyboardButton("🏦 Bank Account", callback_data="withdraw_bank")
            )
            wd_msg = (
                f"┌───── 💸 **WITHDRAWAL** ─────┐\n\n"
                f"🎉 Your balance is ready for payout!\n"
                f"💰 **Balance:** `₹{balance}`\n\n"
                f"👇 **Choose where you want to receive your money:**"
            )
            bot.reply_to(message, wd_msg, parse_mode="Markdown", reply_markup=markup)
        
    elif text == "🎁 Daily Bonus":
        today = date.today()
        if users[user_id]["last_bonus_date"] == today:
            bonus_msg = "🎁 **Daily Reward:** You have already collected today's bonus! Come back tomorrow for a new reward. 🔥"
        else:
            users[user_id]["balance"] += 1
            users[user_id]["last_bonus_date"] = today
            current_bal = users[user_id]["balance"]
            bonus_msg = (
                f"🎉 **CONGRATULATIONS!** 🎉\n\n"
                f"🎁 You have successfully collected your **₹1** Daily Bonus!\n"
                f"💰 **New Balance:** `₹{current_bal}`\n\n"
                f"✨ Come back tomorrow for your next bonus!"
            )
        bot.reply_to(message, bonus_msg, parse_mode="Markdown")
        
    elif text == "⚙️ Account & UPI":
        method = users[user_id]["payout_method"]
        details = users[user_id]["payout_details"]
        acc_msg = (
            f"┌───── ⚙️ **ACCOUNT SETTINGS** ─────┐\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"💳 **Saved Method:** `{method}`\n"
            f"📄 **Details:** `{details}`\n\n"
            f"👇 Click below to set or update your details:"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✏️ Set UPI ID", callback_data="withdraw_upi"),
            types.InlineKeyboardButton("✏️ Set Bank Account", callback_data="withdraw_bank")
        )
        bot.reply_to(message, acc_msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["withdraw_upi", "withdraw_bank"])
def callback_withdrawal_choice(call):
    user_id = call.from_user.id
    if call.data == "withdraw_upi":
        user_states[user_id] = "waiting_for_upi"
        bot.send_message(call.message.chat.id, "📱 **Please send your UPI ID:**\n(Example: `yourname@paytm` or `ybl`)", parse_mode="Markdown")
    elif call.data == "withdraw_bank":
        user_states[user_id] = "waiting_for_bank"
        bot.send_message(call.message.chat.id, "🏦 **Please send your Bank Details:**\n(Format: `A/C No, IFSC Code, Name`)", parse_mode="Markdown")

if __name__ == '__main__':
    # Start Flask keep-alive server in background
    keep_alive()
    
    while True:
        try:
            print("Bot is running...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error occurred: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)
            
