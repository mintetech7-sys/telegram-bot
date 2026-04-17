import telebot
import os
import json
from telebot.types import ReplyKeyboardMarkup, LabeledPrice

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN") or "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

# 👑 ADMIN
ADMIN_ID = 6161012228
CHANNEL = "@minteorg"

# 💾 USER STORAGE ONLY
DATA_FILE = "users.json"
users = {}

# 📦 FILE STORAGE (IN MEMORY)
jps_files = []
style_files = []
new_files = []
set_files = []

# 📥 UPLOAD MODE (IMPORTANT FIX: use user_id, NOT chat_id)
upload_mode = {}

# =========================
# 💾 SAVE / LOAD USERS
# =========================
def save():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def load():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            users = json.load(f)

# =========================
# 👤 USERS
# =========================
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

# =========================
# 👑 ADMIN CHECK
# =========================
def is_admin(msg):
    return msg.from_user.id == ADMIN_ID

# =========================
# 📥 UPLOAD MODE (FIXED)
# =========================
@bot.message_handler(commands=['upload_jps'])
def up_jps(m):
    if m.from_user.id == ADMIN_ID:
        upload_mode[m.from_user.id] = "jps"
        bot.reply_to(m, "📥 Send JPS file now")

@bot.message_handler(commands=['upload_styles'])
def up_styles(m):
    if m.from_user.id == ADMIN_ID:
        upload_mode[m.from_user.id] = "styles"
        bot.reply_to(m, "📥 Send Style file now")

@bot.message_handler(commands=['upload_new'])
def up_new(m):
    if m.from_user.id == ADMIN_ID:
        upload_mode[m.from_user.id] = "new"
        bot.reply_to(m, "📥 Send New file now")

@bot.message_handler(commands=['upload_set'])
def up_set(m):
    if m.from_user.id == ADMIN_ID:
        upload_mode[m.from_user.id] = "set"
        bot.reply_to(m, "📥 Send Set file now")

# =========================
# 📄 RECEIVE FILE (FIXED LOGIC)
# =========================
@bot.message_handler(content_types=['document'])
def get_file(m):
    if m.from_user.id != ADMIN_ID:
        return

    mode = upload_mode.get(m.from_user.id)

    if not mode:
        bot.reply_to(m, "⚠️ No upload mode selected")
        return

    file_id = m.document.file_id

    if mode == "jps":
        jps_files.append(file_id)
    elif mode == "styles":
        style_files.append(file_id)
    elif mode == "new":
        new_files.append(file_id)
    elif mode == "set":
        set_files.append(file_id)

    bot.reply_to(m, f"✅ Saved in {mode} storage")

# =========================
# 📤 SEND FILES
# =========================
def send_files(chat_id, files, uid):
    if not files:
        bot.send_message(chat_id, "❌ No files available")
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

    bot.send_message(m.chat.id, "🚀 SYSTEM ONLINE", reply_markup=kb)

# =========================
# 🆓 FILE BUTTONS
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
# 📥 JPS (simple test version)
# =========================
@bot.message_handler(func=lambda m: m.text == "🎹 JPS ⭐")
def jps(m):
    if check_join(m):
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
        f"""📊 ADMIN PANEL

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
print("🚀 ULTIMATE STABLE BOT RUNNING")
bot.infinity_polling()
