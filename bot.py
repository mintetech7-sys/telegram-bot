import telebot
import os
from telebot.types import ReplyKeyboardMarkup, LabeledPrice

# 🔐 Railway token
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# 👑 Admin
ADMIN_ID = 6161012228
FORCE_CHANNEL = "@minteorg"

# 📦 Storage
jps_files = []
style_files = []
new_files = []
set_files = []
upload_mode = {}


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
        bot.send_message(message.chat.id, f"🚫 Please join {FORCE_CHANNEL} first")
        return False
    return True


# 📥 Upload commands
@bot.message_handler(commands=['upload_jps'])
def upload_jps(message):
    if is_admin(message):
        upload_mode[message.chat.id] = 'jps'
        bot.reply_to(message, '📥 Send JPS file now')


@bot.message_handler(commands=['upload_styles'])
def upload_styles(message):
    if is_admin(message):
        upload_mode[message.chat.id] = 'styles'
        bot.reply_to(message, '📥 Send Style file now')


@bot.message_handler(commands=['upload_new'])
def upload_new(message):
    if is_admin(message):
        upload_mode[message.chat.id] = 'new'
        bot.reply_to(message, '📥 Send New file now')


@bot.message_handler(commands=['upload_set'])
def upload_set(message):
    if is_admin(message):
        upload_mode[message.chat.id] = 'set'
        bot.reply_to(message, '📥 Send Set file now')


# 📄 Receive files
@bot.message_handler(content_types=['document'])
def get_file(message):
    if not is_admin(message):
        bot.reply_to(message, "🚫 Admin only")
        return

    category = upload_mode.get(message.chat.id)
    if not category:
        bot.reply_to(message, "⚠️ Choose upload mode first")
        return

    file_id = message.document.file_id

    if category == 'jps':
        jps_files.append(file_id)
    elif category == 'styles':
        style_files.append(file_id)
    elif category == 'new':
        new_files.append(file_id)
    elif category == 'set':
        set_files.append(file_id)

    bot.reply_to(message, f"✅ Saved to {category.upper()}")


# ▶️ Start menu
@bot.message_handler(commands=['start'])
def start(message):
    if not check_join(message):
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎹 JPS", "🎼 Styles")
    markup.add("🆕 New", "⚙️ Set")
    bot.send_message(message.chat.id, "⭐ ORG BOT STORE READY", reply_markup=markup)


# 💳 Paid JPS
@bot.message_handler(func=lambda m: m.text == "🎹 JPS")
def buy_jps(message):
    if not check_join(message):
        return

    prices = [LabeledPrice("All JPS Files", 100)]
    bot.send_invoice(
        message.chat.id,
        title="🎹 All JPS Pack",
        description="Unlock all JPS files",
        invoice_payload="all_jps",
        provider_token="",
        currency="XTR",
        prices=prices
    )


# 💳 Paid Style
@bot.message_handler(func=lambda m: m.text == "🎼 Styles")
def buy_style(message):
    if not check_join(message):
        return

    prices = [LabeledPrice("One Style", 5)]
    bot.send_invoice(
        message.chat.id,
        title="🎼 Premium Style",
        description="Unlock one style file",
        invoice_payload="one_style",
        provider_token="",
        currency="XTR",
        prices=prices
    )


# 🆓 Free sections
@bot.message_handler(func=lambda m: m.text == "🆕 New")
def new_files_send(message):
    if not check_join(message):
        return
    for f in new_files:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "⚙️ Set")
def set_files_send(message):
    if not check_join(message):
        return
    for f in set_files:
        bot.send_document(message.chat.id, f)


# 💳 Payment checks
@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(pre_checkout_q):
    bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    payload = message.successful_payment.invoice_payload

    if payload == "all_jps":
        for f in jps_files:
            bot.send_document(message.chat.id, f)

    elif payload == "one_style":
        if style_files:
            bot.send_document(message.chat.id, style_files[0])


print("✅ ORG paid bot running...")
bot.polling(none_stop=True)
