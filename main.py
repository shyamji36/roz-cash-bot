import telebot
from telebot import types

# Bot Token aur Username
TOKEN = '9126975810:AAFthAtAMIcT5_giUKAnNnIUuI2_TrDh74k'
BOT_USERNAME = 'Roz_Cash_Bot'

bot = telebot.TeleBot(TOKEN)

# In-memory databases (Temporary storage for user data)
users = {}
balances = {}
referrals = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Register user if new
    if user_id not in users:
        users[user_id] = {
            'first_name': message.from_user.first_name,
            'username': message.from_user.username
        }
        balances[user_id] = 0.0
        referrals[user_id] = 0
        
        # Handle Referral if joined via link
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if referrer_id != user_id and referrer_id in users:
                    referrals[referrer_id] += 1
                    balances[referrer_id] += 2.0  # ₹2 per referral bonus
                    bot.send_message(referrer_id, f"🎉 **Aapko naya referral mila hai!**\nBonus: ₹2.00 add ho gaye hain.")
            except ValueError:
                pass

    # Main Menu Markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Balance"),
        types.KeyboardButton("👥 Refer & Earn"),
        types.KeyboardButton("💸 Withdraw"),
        types.KeyboardButton("ℹ️ Help")
    )

    welcome_text = (
        f"👋 **Welcome to Roz Cash Bot, {message.from_user.first_name}!**\n\n"
        f"Yahan aap doston ko refer karke aur daily rewards ke zariye paise kama sakte hain.\n"
        f"Neeche diye gaye buttons ka istemaal karein."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if text == "💰 Balance":
        bal = balances.get(user_id, 0.0)
        refs = referrals.get(user_id, 0)
        msg = (
            f"👤 **Aapki Account Details:**\n\n"
            f"💵 **Current Balance:** ₹{bal:.2f}\n"
            f"👥 **Total Referrals:** {refs} users"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "👥 Refer & Earn":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        msg = (
            f"🔗 **Aapka Referral Link:**\n`{ref_link}`\n\n"
            f"Is link ko apne doston ke sath share karein. Har ek join par aapko **₹2** milenge!"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "💸 Withdraw":
        bal = balances.get(user_id, 0.0)
        if bal < 10.0:
            bot.send_message(message.chat.id, f"❌ Minimum withdrawal limit **₹10.00** hai.\nAapka current balance ₹{bal:.2f} hai.")
        else:
            bot.send_message(message.chat.id, "✅ Withdrawal request accept ho gayi hai! Jaldi hi amount aapke account mein bhej diya jayega.")
            balances[user_id] = 0.0  # Reset balance after withdrawal

    elif text == "ℹ️ Help":
        help_text = (
            "💡 **Madad ke liye:**\n\n"
            "1. **Refer & Earn:** Apne doston ko invite karein.\n"
            "2. **Balance Check:** Apna earn kiya hua paisa dekhein.\n"
            "3. **Withdraw:** Minimum ₹10 hone par UPI ya Bank mein withdraw karein."
        )
        bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# Bot ko continuously run karne ke liye
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
  
