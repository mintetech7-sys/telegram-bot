import telebot
import os
import pickle
from telebot.types import ReplyKeyboardMarkup, LabeledPrice

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# 👑 ADMIN
ADMIN_ID = 6161012228
FORCE_CHANNEL = "@minteorg"

# 📦 STORAGE (NO DB)
BACKUP_FILE = "backup.dat"

jps_files = []
style_files = []
new_files = []
set_files = []

users = {}

# =========================
# 💾 BACKUP SYSTEM
# =========================
def save_backup():
    data = {
        "jps": jps_files,
        "styles": style_files,
        "new": new_files,
        "set": set_files,
        "users": users
    }
    with open(BACKUP_FILE, "wb") as f:
        pickle.dump(data, f)

def load_backup():
    global jps_files, style_files, new_files, set_files, users

    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "rb") as f:
                data = pickle.load(f)

            jps_files = data.get("jps", [])
            style_files = data.get("styles", [])
            new_files = data.get("new", [])
            set_files = data.get("set", [])
            users = data.get("users", {})
        except:
            pass

# =========================
# 👤 USER SYSTEM
# =========================
def add_user(user_id):
    if user_id not in users:
        users[user_id] = {"downloads": 0, "vip": 0}
        save_backup()

def is_vip(user_id):
    return users.get(user_id, {}).get("vip", 0) == 1

def can_download(user_id):
    if is_vip(user_id):
        return True
    return users.get(user_id, {}).get("downloads", 0) < 3

def add_download(user_id):
    if user_id in users:
        users[user_id]["downloads"] += 1
        save_backup()

def set_vip(user_id):
    if user_id in users:
        users[user_id]["vip"] = 1
        save_backup()

def get_user_count():
    return len(users)

# =========================
# 🔐 FORCE JOIN
# =========================
def joined_channel(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def check_join(message):
    if not joined_channel(message.from_user.id):
        bot.send_message(message.chat.id, f"🚫 Join {FORCE_CHANNEL} first")
        return False
    return True

# =========================
# 👑 ADMIN CHECK
# =========================
def is_admin(message):
    return message.from_user.id == ADMIN_ID

# =========================
# 📥 UPLOAD MODE
# =========================
upload_mode = {}

@bot.message_handler(commands=['upload_jps'])
def up_jps(m):
    if is_admin(m):
        upload_mode[m.chat.id] = "jps"
        bot.reply_to(m, "📥 Send JPS file (5⭐ STAR CONTENT)")

@bot.message_handler(commands=['upload_styles'])
def up_styles(m):
    if is_admin(m):
        upload_mode[m.chat.id] = "styles"
        bot.reply_to(m, "📥 Send Style file")

@bot.message_handler(commands=['upload_new'])
def up_new(m):
    if is_admin(m):
        upload_mode[m.chat.id] = "new"
        bot.reply_to(m, "📥 Send New file")

@bot.message_handler(commands=['upload_set'])
def up_set(m):
    if is_admin(m):
        upload_mode[m.chat.id] = "set"
        bot.reply_to(m, "📥 Send Set file")

# =========================
# 📄 RECEIVE FILES
# =========================
@bot.message_handler(content_types=['document'])
def get_file(message):
    if not is_admin(message):
        return

    mode = upload_mode.get(message.chat.id)
    if not mode:
        return

    file_id = message.document.file_id

    if mode == "jps":
        jps_files.append(file_id)
    elif mode == "styles":
        style_files.append(file_id)
    elif mode == "new":
        new_files.append(file_id)
    elif mode == "set":
        set_files.append(file_id)

    save_backup()
    bot.reply_to(message, "✅ File saved safely")

# =========================
# ▶️ START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)

    if not check_join(message):
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎹 JPS (⭐ STAR)", "🎼 Styles")
    markup.add("🆕 New", "⚙️ Set")

    bot.send_message(message.chat.id, "⭐ SAFE STORE READY", reply_markup=markup)

# =========================
# ⭐ TELEGRAM STARS PAYMENT (JPS)
# =========================
@bot.message_handler(func=lambda m: m.text == "🎹 JPS (⭐ STAR)")
def jps_buy(message):
    if not check_join(message):
        return

    bot.send_invoice(
        chat_id=message.chat.id,
        title="JPS PACK (PREMIUM)",
        description="⭐ Telegram Stars Content Pack",
        invoice_payload="jps_all",
        provider_token="",  # REQUIRED EMPTY FOR STARS
        currency="XTR",     # ⭐ Telegram Stars currency
        prices=[LabeledPrice("JPS Pack", 5)]  # 5 stars
    )

# =========================
# 🆓 FILES (FREE)
# =========================
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
def set_files_send(message):
    if not check_join(message):
        return
    for f in set_files:
        bot.send_document(message.chat.id, f)

# =========================
# ⭐ PAYMENT SUCCESS
# =========================
@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def success(message):
    if message.successful_payment.invoice_payload == "jps_all":
        for f in jps_files:
            bot.send_document(message.chat.id, f)

# =========================
# 📡 ADMIN PANEL
# =========================
@bot.message_handler(commands=['admin'])
def admin(message):
    if not is_admin(message):
        return

    bot.send_message(
        message.chat.id,
        f"""
📡 ADMIN PANEL

👤 Users: {get_user_count()}
💎 VIP users: {sum(1 for u in users.values() if u['vip'] == 1)}
📦 JPS files: {len(jps_files)}
🎼 Styles: {len(style_files)}
🆕 New: {len(new_files)}
⚙️ Set: {len(set_files)}
"""
    )

# =========================
# 🚀 START BOT
# =========================
load_backup()
print("🚀 STAR-BASED BOT RUNNING...")
bot.polling(none_stop=True)
