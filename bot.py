import telebot
import os
import json
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6161012228
DB_FILE = "files.json"
USERS_FILE = "users.json"
REQUIRED_CHANNEL = "@yourchannelusername"  # change this


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


files = load_json(DB_FILE, {
    "jps": [],
    "styles": [],
    "new": [],
    "set": []
})

users = load_json(USERS_FILE, [])


def is_admin(message):
    return message.from_user.id == ADMIN_ID


def check_join(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # 👥 save unique users
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

    # ⭐ force channel join
    if not check_join(user_id):
        bot.send_message(
            message.chat.id,
            f"⭐ Please join {REQUIRED_CHANNEL} first, then press /start again"
        )
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎹 JPS", "🎼 Styles")
    markup.add("🆕 New", "⚙️ Set")
    bot.send_message(
        message.chat.id,
        f"🎹 ORG BOT READY\n👥 Total users: {len(users)}",
        reply_markup=markup
    )


@bot.message_handler(commands=['stats'])
def stats(message):
    if not is_admin(message):
        return
    bot.send_message(message.chat.id, f"👥 Total users: {len(users)}")


@bot.message_handler(content_types=['document'])
def upload_file(message):
    if not is_admin(message):
        bot.reply_to(message, "🚫 Admin only")
        return

    file_id = message.document.file_id
    files["jps"].append(file_id)
    save_json(DB_FILE, files)
    bot.reply_to(message, "✅ File saved permanently in JPS")


@bot.message_handler(func=lambda m: m.text == "🎹 JPS")
def jps(message):
    for f in files["jps"]:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "🎼 Styles")
def styles(message):
    for f in files["styles"]:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "🆕 New")
def new(message):
    for f in files["new"]:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "⚙️ Set")
def setf(message):
    for f in files["set"]:
        bot.send_document(message.chat.id, f)


print("🚀 Bot running...")
bot.polling(none_stop=True)
