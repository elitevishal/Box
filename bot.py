# -*- coding: utf-8 -*-
"""
Telegram Premium Force-Sub & Utility Bot
Features:
- Channels displayed 2 per row (Grid layout)
- Verification remembered (Database / persistent check so joined users never see join prompt again)
- Premium UI with stylish buttons and emojis
- Built-in Flask web server for 24/7 hosting (Render, Koyeb, Heroku, VPS)
"""

import os
import sqlite3
import threading
from flask import Flask, render_template, jsonify
import telebot
from telebot import types

# ================= CONFIGURATION =================
# Apne Bot ka Token yaha dalein ya Environment Variable set karein
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9057540528:AAHA3zbRfTvOdYA23ESw43QziYP_qA0_Xqw")

# Channels list: (Username ya ID, Display Name, Invite Link)
# Ek row me 2 buttons dikhane ke liye channels ko define karein
CHANNELS = [
    {"name": "Elite Vishal", "url": "https://t.me/elitevishal", "chat_id": "@elitevishal"},
    {"name": "Elite VIP Channel", "url": "https://t.me/+dmaFFBHLSj9jZTQ9", "chat_id": None},
    {"name": "Elite Bro", "url": "https://t.me/elitebroooo", "chat_id": "@elitebroooo"},
    {"name": "Elite Team Backup", "url": "https://t.me/eliteteambackup", "chat_id": "@eliteteambackup"}
]

# Admin Telegram IDs (Access to admin controls)
ADMIN_IDS = [8266427252]

# ================= DATABASE SETUP =================
DB_PATH = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            is_verified INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_user_verified(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0] == 1)

def set_user_verified(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, is_verified)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            is_verified = 1,
            username = excluded.username,
            first_name = excluded.first_name
    """, (user_id, username or "", first_name or ""))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_verified = 1")
    verified = cursor.fetchone()[0]
    conn.close()
    return {"total_users": total, "verified_users": verified}

# Initialize Database
init_db()

# ================= BOT INITIALIZATION =================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Helper function: Check if user actually joined all channels
def check_user_joined_all(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            # Agar bot channel me admin nahi hai ya channel accessible nahi hai
            print(f"[Error checking {channel['id']}]: {e}")
            return False
    return True

# Premium Keyboards
def get_join_keyboard():
    markup = types.InlineKeyboardMarkup()
    
    # Buttons ko 2-2 ke pair me add karna (2 per row)
    buttons = []
    for ch in REQUIRED_CHANNELS:
        btn = types.InlineKeyboardButton(text=f"✨ {ch['name']}", url=ch["url"])
        buttons.append(btn)
    
    # 2 buttons per row slice & add
    for i in range(0, len(buttons), 2):
        row_buttons = buttons[i:i+2]
        markup.row(*row_buttons)
    
    # Bottom me Verify Button (Full Width)
    verify_btn = types.InlineKeyboardButton(text="✅ Verify / Join Ho Gaya", callback_data="check_joined")
    markup.add(verify_btn)
    return markup

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🚀 Features", callback_data="menu_features")
    btn2 = types.InlineKeyboardButton("💎 Premium Perks", callback_data="menu_perks")
    btn3 = types.InlineKeyboardButton("📊 My Stats", callback_data="menu_stats")
    btn4 = types.InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
    btn_support = types.InlineKeyboardButton("💬 Support & Community", url="https://t.me/your_support_link")
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.add(btn_support)
    return markup

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    # Agar user pehle se verify ho chuka hai database me
    if is_user_verified(user_id):
        text = (
            f"👑 <b>Welcome Back, {first_name}!</b>

"
            f"⚡ <i>Aapka verification pehle se complete hai.</i>

"
            f"Aap bot ke sabhi premium features directly access kar sakte hain. "
            f"Neeche diye gaye options me se select karein:"
        )
        bot.send_message(message.chat.id, text, reply_markup=get_main_menu_keyboard())
        return

    # Agar user verify nahi hai to channel join karwayenge (2 per row layout)
    text = (
        f"👋 <b>Namaste {first_name}!</b>

"
        f"🔐 <b>Access Restricted:</b>
"
        f"Bot ka use karne ke liye aapko hamare official channels join karne honge.

"
        f"👇 <i>Neeche diye channels ko join karke <b>Verify</b> button par click karein:</i>"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_join_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def handle_verification(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name
    username = call.from_user.username

    # Check live status in all channels
    if check_user_joined_all(user_id):
        # Database me record update karo taaki dobara /start par channel na mangey
        set_user_verified(user_id, username, first_name)
        
        bot.answer_callback_query(call.id, "🎉 Verification Successful!", show_alert=True)
        
        success_text = (
            f"🎉 <b>Badhai Ho {first_name}! Verification Complete!</b>

"
            f"✅ Aapne sabhi channels join kar liye hain.
"
            f"Ab aapko dobara channels join karne ki jarurat nahi padegi.

"
            f"🌟 <b>Welcome to Premium Dashboard:</b>"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Aapne abhi tak sabhi channels join nahi kiye! Kripya sabhi channels join karke firse click karein.",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def handle_menu_callbacks(call):
    action = call.data
    if action == "menu_features":
        text = "⚡ <b>Features:</b>\n\n1. High Speed Processing\n2. 24/7 Online Uptime\n3. Auto Join Verification Memory\n4. Custom Dashboard Integration"
    elif action == "menu_perks":
        text = "💎 <b>Premium Perks:</b>\n\n• Zero Ads\n• Direct Admin Support\n• Priority Queue Execution"
    elif action == "menu_stats":
        stats = get_stats()
        text = f"📊 <b>Bot Stats:</b>\n\n• Total Registered: {stats['total_users']}\n• Verified Members: {stats['verified_users']}"
    elif action == "menu_settings":
        text = "⚙️ <b>Settings:</b>\n\nAapke notifications aur preferences active hain."
    else:
        text = "Option under development."

    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=back_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def handle_back_menu(call):
    text = (
        f"👑 <b>Main Dashboard</b>

"
        f"Aap bot ke features neeche diye gaye buttons se browse kar sakte hain:"
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=get_main_menu_keyboard()
    )

# ================= FLASK WEB SERVER (24/7 Uptime) =================
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    stats = get_stats()
    return render_template("dashboard.html", stats=stats)

@app.route("/health")
def health():
    return jsonify({"status": "running", "bot": "online"}), 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= MAIN RUNNER =================
if __name__ == "__main__":
    print("🚀 Starting Web Server on Port 8080...")
    web_thread = threading.Thread(target=run_flask)
    web_thread.daemon = True
    web_thread.start()

    print("🤖 Bot is polling now...")
    bot.infinity_polling(skip_pending=True)
