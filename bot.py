import telebot
import os
from telebot.types import ReplyKeyboardMarkup

# 🔐 Token from Railway
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN not found")
    exit()

# 👑 YOUR ADMIN ID (change this!)
ADMIN_ID = 6161012228

# 📦 File storage (start empty)
jps_files = []
style_files = []
new_files = []
set_files = []

# 🔐 check admin
def is_admin(message):
    return message.from_user.id == ADMIN_ID

# 🔘 start button menu
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("🎹 JPS", "🎼 Styles")
    markup.add("🆕 New", "⚙️ Set")

    bot.send_message(message.chat.id, "🎹 ORG BOT READY", reply_markup=markup)

# 👑 admin upload file_id generator
@bot.message_handler(content_types=['document'])
def get_file_id(message):
    if not is_admin(message):
        bot.reply_to(message, "🚫 Admin only")
        return

    file_id = message.document.file_id
    bot.reply_to(message, f"FILE ID:\n{file_id}")

# 🎹 JPS
@bot.message_handler(func=lambda m: m.text == "🎹 JPS")
def jps(message):
    for f in jps_files:
        bot.send_document(message.chat.id, f)

# 🎼 Styles
@bot.message_handler(func=lambda m: m.text == "🎼 Styles")
def styles(message):
    for f in style_files:
        bot.send_document(message.chat.id, f)

# 🆕 New
@bot.message_handler(func=lambda m: m.text == "🆕 New")
def new(message):
    for f in new_files:
        bot.send_document(message.chat.id, f)

# ⚙️ Set
@bot.message_handler(func=lambda m: m.text == "⚙️ Set")
def setf(message):
    for f in set_files:
        bot.send_document(message.chat.id, f)

print("Bot running...")
bot.polling(none_stop=True, interval=0, timeout=20)
