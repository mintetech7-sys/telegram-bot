import telebot
from telebot.types import ReplyKeyboardMarkup

# 🔐 Bot token
TOKEN = "7951915115:AAEXPj5IgrBsJpY3TaePejMA5u_EF5p_ri8"
bot = telebot.TeleBot(TOKEN)

# 👑 Admin
ADMIN_ID = 6161012228

# 📢 Force join channel username
FORCE_CHANNEL = "@minteorg"

# 📦 File storage
jps_files = []
style_files = []
new_files = []
set_files = []


def is_admin(message):
    return message.from_user.id == ADMIN_ID


def joined_channel(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def check_join(message):
    if not joined_channel(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"🚫 Please join {FORCE_CHANNEL} first to use this bot."
        )
        return False
    return True


@bot.message_handler(commands=['start'])
def start(message):
    if not check_join(message):
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎹 JPS", "🎼 Styles")
    markup.add("🆕 New", "⚙️ Set")

    bot.send_message(message.chat.id, "⭐ ORG BOT READY", reply_markup=markup)


@bot.message_handler(content_types=['document'])
def get_file_id(message):
    if not is_admin(message):
        bot.reply_to(message, "🚫 Admin only")
        return

    file_id = message.document.file_id
    bot.reply_to(message, f"FILE ID:\n{file_id}")


@bot.message_handler(func=lambda m: m.text == "🎹 JPS")
def jps(message):
    if not check_join(message):
        return
    for f in jps_files:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "🎼 Styles")
def styles(message):
    if not check_join(message):
        return
    for f in style_files:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "🆕 New")
def new(message):
    if not check_join(message):
        return
    for f in new_files:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "⚙️ Set")
def setf(message):
    if not check_join(message):
        return
    for f in set_files:
        bot.send_document(message.chat.id, f)


print("✅ Bot running with auto join check...")
bot.polling(none_stop=True)
