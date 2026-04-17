import telebot
import os
import json
from telebot.types import ReplyKeyboardMarkup, LabeledPrice

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6161012228
CHANNEL = "@minteorg"

DATA_FILE = "users.json"
users = {}

# =========================
# 💾 USERS
# =========================
def save():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def load():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            users = json.load(f)

def add_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"downloads": 0}
        save()

def add_download(uid):
    uid = str(uid)
    if uid in users:
        users[uid]["downloads"] += 1
        save()

def total_downloads():
    return sum(u["downloads"] for u in users.values())

# =========================
# 🔐 JOIN CHECK
# =========================
def joined(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status not in ["left", "kicked"]
    except:
        return False

def check_join(msg):
    if not joined(msg.from_user.id):
        bot.send_message(msg.chat.id, f"🚫 Join {CHANNEL} first")
        return False
    return True

def is_admin(msg):
    return msg.from_user.id == ADMIN_ID

# =========================
# 📦 FILE LISTS (AUTO)
# =========================
jps_files = []
style_files = []
new_files = []
set_files = []

# =========================
# 🔄 AUTO BUILD FROM CHANNEL
# =========================
@bot.channel_post_handler(content_types=['document'])
def auto_collect(m):
    file_id = m.document.file_id
    caption = (m.caption or "").lower()

    if "#jps" in caption:
        jps_files.append(file_id)
    elif "#style" in caption:
        style_files.append(file_id)
    elif "#new" in caption:
        new_files.append(file_id)
    elif "#set" in caption:
        set_files.append(file_id)

# =========================
# 📥 ADMIN UPLOAD
# =========================
upload_mode = {}

@bot.message_handler(commands=['upload'])
def upload(m):
    if is_admin(m):
        bot.reply_to(m, "Send file with caption:\n#jps / #style / #new / #set")

@bot.message_handler(content_types=['document'])
def receive(m):
    if not is_admin(m):
        return

    # forward to channel
    bot.send_document(CHANNEL, m.document.file_id, caption=m.caption)

    bot.reply_to(m, "✅ Uploaded to storage")

# =========================
# 📤 SEND FILES
# =========================
def send_files(chat_id, files, uid):
    if not files:
        bot.send_message(chat_id, "❌ No files")
        return

    for f in files:
        bot.send_document(chat_id, f)

    add_download(uid)

# =========================
# ▶️ START
# =========================
@bot.message_handler(commands=['start'])
def start(m):
    add_user(m.from_user.id)

    if not check_join(m):
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎹 JPS ⭐", "🎼 Styles")
    kb.add("🆕 New", "⚙️ Set")

    bot.send_message(m.chat.id, "ULTIMATE STORE READY", reply_markup=kb)

# =========================
# ⭐ PAYMENT
# =========================
@bot.message_handler(func=lambda m: m.text == "🎹 JPS ⭐")
def pay(m):
    if not check_join(m):
        return

    bot.send_invoice(
        chat_id=m.chat.id,
        title="JPS PACK",
        description="Premium",
        invoice_payload="jps",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("JPS", 5)]
    )

# =========================
# 🆓 FILES
# =========================
@bot.message_handler(func=lambda m: m.text == "🎼 Styles")
def styles(m):
    if check_join(m):
        send_files(m.chat.id, style_files, m.from_user.id)

@bot.message_handler(func=lambda m: m.text == "🆕 New")
def new(m):
    if check_join(m):
        send_files(m.chat.id, new_files, m.from_user.id)

@bot.message_handler(func=lambda m: m.text == "⚙️ Set")
def setf(m):
    if check_join(m):
        send_files(m.chat.id, set_files, m.from_user.id)

# =========================
# ⭐ SUCCESS
# =========================
@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def success(m):
    if m.successful_payment.invoice_payload == "jps":
        send_files(m.chat.id, jps_files, m.from_user.id)

# =========================
# 📊 ADMIN PANEL
# =========================
@bot.message_handler(commands=['admin'])
def admin(m):
    if not is_admin(m):
        return

    bot.send_message(
        m.chat.id,
        f"""📊 ULTIMATE STATS

👤 Users: {len(users)}
📥 Downloads: {total_downloads()}

🎹 JPS: {len(jps_files)}
🎼 Styles: {len(style_files)}
🆕 New: {len(new_files)}
⚙️ Set: {len(set_files)}
"""
    )

# =========================
# 🚀 RUN
# =========================
load()
print("🚀 ULTIMATE BOT RUNNING")
bot.infinity_polling()
