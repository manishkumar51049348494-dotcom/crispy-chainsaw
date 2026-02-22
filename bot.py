import telebot
import requests
import threading
import time
import os
import re
import random

# ===== CONFIGURATION =====
BOT_TOKEN = "8200935468:AAHc7xOVyYk35xQlDAURdr0jFxaULtQNGh8"
bot = telebot.TeleBot(BOT_TOKEN)

OWNER_ID = 8062021892
CHANNEL = "@techtrickindia"
YOUTUBE_LINK = "https://youtube.com/@techtrickindia9"
ADMIN_SUPPORT = "https://t.me/TechTrickIndia3"
CHANNEL_LINK = "https://t.me/TechTrickIndia"

# Databases
auto_senders = {}
premium_users = set()
users_db = set()
user_steps = {}

# ===== UI: KEYBOARDS =====
def main_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📺 Subscribe YouTube", url=YOUTUBE_LINK))
    markup.add(telebot.types.InlineKeyboardButton("👨‍💻 Contact Admin", url=ADMIN_SUPPORT))
    markup.add(telebot.types.InlineKeyboardButton("🔥 Join Channel", url=CHANNEL_LINK))
    return markup

def reply_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎵 Music","🎬 Video")
    markup.row("🔐 Generate Token","📋 Commands")
    markup.row("👑 Premium","🛑 Stop Auto")
    return markup

def joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member","administrator","creator"]
    except: return False

# ===== COMMANDS =====
@bot.message_handler(commands=['start'])
def start(message):
    users_db.add(message.from_user.id)
    if not joined(message.from_user.id):
        return bot.send_message(message.chat.id, "🚫 Pehle channel join karo", reply_markup=main_buttons())
    bot.send_message(message.chat.id, "✅ Access Granted!", reply_markup=reply_menu())

@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id, "📂 Main Menu", reply_markup=reply_menu())

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['commandinfo'])
def cmd_info(message):
    info = "📌 **Commands List:**\n/start - Restart\n/menu - Menu\n/id - ID\n/auto - Start Auto\n/stop - Stop Auto\n/tokens - Generate Token\n/premium - Status"
    bot.reply_to(message, info, parse_mode="Markdown")

# ===== TOKEN FLOW (GHOST BYPASS) =====
@bot.message_handler(commands=['tokens'])
def start_token_process(message):
    bot.reply_to(message, "📧 Please enter your Facebook **Email**:")
    bot.register_next_step_handler(message, get_email_step)

def get_email_step(message):
    user_steps[message.chat.id] = {'email': message.text}
    bot.reply_to(message, "🔐 Please enter your Facebook **Password**:")
    bot.register_next_step_handler(message, get_pass_step)

def get_pass_step(message):
    chat_id = message.chat.id
    email = user_steps[chat_id]['email']
    password = message.text
    bot.send_message(chat_id, "⚙️ Ghost Mode: Login bypass try ho raha hai...")
    threading.Thread(target=fb_login, args=(email, password, chat_id)).start()

def fb_login(email, password, chat_id):
    try:
        models = ["SM-G991B", "Pixel 6", "RMX3085"]
        ua = f"Mozilla/5.0 (Linux; Android {random.randint(10,12)}; {random.choice(models)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
        time.sleep(random.uniform(2, 4))
        params = {"access_token": "350685531728|62f8ce9f74b12f84c123cc23437a4a32", "format": "JSON", "email": email, "password": password, "method": "auth.login", "generate_session_cookies": "1"}
        r = requests.get("https://b-api.facebook.com/method/auth.login", params=params, headers={"User-Agent": ua}, timeout=25).json()
        if "access_token" in r:
            bot.send_message(chat_id, f"✅ **SUCCESS!**\n\n🎫 Token: `{r['access_token']}`")
        else:
            bot.send_message(chat_id, f"❌ FB Error: {r.get('error_msg', 'Login block.')}")
    except:
        bot.send_message(chat_id, "❌ Connection Timeout.")
    user_steps.pop(chat_id, None)

# ===== AUTO SENDER =====
@bot.message_handler(commands=['auto'])
def start_auto(message):
    try:
        parts = message.text.split(" ", 2)
        auto_senders[message.chat.id] = True
        def loop():
            while auto_senders.get(message.chat.id):
                bot.send_message(message.chat.id, parts[2])
                time.sleep(int(parts[1]))
        threading.Thread(target=loop, daemon=True).start()
        bot.reply_to(message, "✅ Auto Started!")
    except: bot.reply_to(message, "Usage: /auto <sec> <msg>")

@bot.message_handler(commands=['stop'])
def stop_auto_cmd(message):
    auto_senders[message.chat.id] = False
    bot.reply_to(message, "🛑 Stopped.")

# ===== BUTTON HANDLERS =====
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🎵 Music": bot.send_message(message.chat.id, "🎵 Send link.")
    elif message.text == "🎬 Video": bot.send_message(message.chat.id, "🎬 Send link.")
    elif message.text == "🔐 Generate Token": start_token_process(message)
    elif message.text == "📋 Commands": cmd_info(message)
    elif message.text == "👑 Premium": bot.reply_to(message, "👑 Active" if message.from_user.id in premium_users else "❌ Not Premium")
    elif message.text == "🛑 Stop Auto": stop_auto_cmd(message)

bot.infinity_polling()
