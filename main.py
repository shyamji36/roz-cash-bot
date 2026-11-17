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

# Telegram Bot Token
TOKEN = '9126975810:AAHD34l3tnFgh6pmCS8zgf203kqkGb-s_cY'
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user data
users = {}

# Track user states (for setting UPI, Bank details or Deposit)
user_states = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_balance = types.KeyboardButton("💰 My Balance")
    btn_ref = types.KeyboardButton("🚀 Refer & Earn")
    btn_withdraw = types.KeyboardButton("💸 Withdraw Money")
    btn_deposit = types.KeyboardButton("💳 Deposit Money")  # Deposit Button Added Here
    btn_faucet = types.KeyboardButton("🚰 Daily Faucet")
    btn_account = types.KeyboardButton("⚙️ Account & UPI")
    markup.add(btn_balance, btn_ref)
    markup.add(btn_withdraw, btn_deposit)
    markup.add(btn_faucet, btn_account)
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

    elif state == "waiting_for_deposit_proof":
        user_states[user_id] = None
        bot.reply_to(
            message, 
            "✅ **Deposit Request Submitted!**\nAdmin verify karne ke baad aapke wallet mein balance add kar diya jayega.", 
            parse_mode="Markdown", 
            reply_markup=get_main_keyboard()
        )
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
            
    elif text == "💳 Deposit Money":
        deposit_msg = (
            f"💳 **DEPOSIT FUNDS** 💳\n\n"
            f"Apne account mein balance add karne ke liye niche diye gaye UPI ID par payment karein:\n\n"
            f"📌 **UPI ID:** `shyamji@upi`\n"
            f"(Ya QR code par scan karein)\n\n"
            f"⚠️ Payment karne ke baad apna **UTR Number / Transaction Reference** yahan bhej dein."
        )
        user_states[user_id] = "waiting_for_deposit_proof"
        bot.reply_to(message, deposit_msg, parse_mode="Markdown")
        
    elif text == "🚰 Daily Faucet":
        faucet_msg = (
            f"🚰 **DAILY FAUCET & REWARDS** 🚰\n\n"
            f"Claim your daily rewards and participate in exclusive contests to boost your earnings!\n\n"
            f"👇 Choose an option below:"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎁 Claim Daily Bonus (₹1)", callback_data="claim_daily_bonus"),
            types.InlineKeyboardButton("📢 Share & Earn", callback_data="share_and_earn"),
            types.InlineKeyboardButton("🏆 Daily Referral Contest", callback_data="daily_ref_contest")
        )
        bot.reply_to(message, faucet_msg, parse_mode="Markdown", reply_markup=markup)
        
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

@bot.callback_query_handler(func=lambda call: call.data in ["withdraw_upi", "withdraw_bank", "claim_daily_bonus", "share_and_earn", "daily_ref_contest"])
def callback_handler(call):
    user_id = call.message.chat.id
    data = call.data
    
    if data == "withdraw_upi":
        user_states[call.from_user.id] = "waiting_for_upi"
        bot.send_message(user_id, "📱 **Please send your UPI ID:**\n(Example: `yourname@paytm` or `ybl`)", parse_mode="Markdown")
        
    elif data == "withdraw_bank":
        user_states[call.from_user.id] = "waiting_for_bank"
        bot.send_message(user_id, "🏦 **Please send your Bank Details:**\n(Format: `A/C No, IFSC Code, Name`)", parse_mode="Markdown")
        
    elif data == "claim_daily_bonus":
        today = date.today()
        if users[user_id]["last_bonus_date"] == today:
            bot.answer_callback_query(call.id, "⚠️ Already claimed today!", show_alert=True)
            bot.send_message(user_id, "🎁 **Daily Reward:** You have already collected today's bonus! Come back tomorrow. 🔥", parse_mode="Markdown")
        else:
            users[user_id]["balance"] += 1
            users[user_id]["last_bonus_date"] = today
            current_bal = users[user_id]["balance"]
            bot.answer_callback_query(call.id, "🎉 +₹1 Bonus Claimed!", show_alert=True)
            bot.send_message(
                user_id,
                f"🎉 **CONGRATULATIONS!** 🎉\n\n"
                f"🎁 You successfully collected your **₹1** Daily Faucet Bonus!\n"
                f"💰 **New Balance:** `₹{current_bal}`",
                parse_mode="Markdown"
            )
            
    elif data == "share_and_earn":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={call.from_user.id}"
        share_text = (
            f"📢 **SHARE & EARN**\n\n"
            f"Apne dosto ko WhatsApp, Telegram aur Facebook groups par share karein aur har join par instant ₹3 payein!\n\n"
            f"🔗 Aapka Link:\n`{ref_link}`"
        )
        bot.send_message(user_id, share_text, parse_mode="Markdown")
        
    elif data == "daily_ref_contest":
        contest_text = (
            f"🏆 **DAILY REFERRAL CONTEST** 🏆\n\n"
            f"Top referrers of the day win special cash prizes!\n\n"
            f"🥇 1st Rank: **₹500 Extra**\n"
            f"🥈 2nd Rank: **₹250 Extra**\n"
            f"🥉 3rd Rank: **₹100 Extra**\n\n"
            f"🚀 Contest daily reset hota hai. Zyada refer karein aur leaderboard par aayein!"
        )
        bot.send_message(user_id, contest_text, parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    while True:
        try:
            print("Bot is running...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error occurred: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)
            
