# wormgpt_telegram_bot.py
# FINAL FIXED VERSION - Multi-user support, no "message text is empty" error, long replies as .txt, everything else intact

import telebot
import time
import logging
from collections import defaultdict, deque
from io import BytesIO
from groq import Groq
import json
import os
import re

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────
BOT_TOKEN = "7500596128:AAGaT2OipZCktPEGHzjkbjdjfdvjfbvjkdNG9CZihUrxg"
ADMIN_ID = 8000000000
GROQ_API_KEY = "your_groq_api_key"
MODEL = "llama-3.3-70b-versatile"
LOG_CHANNEL_ID = -10020000000  # Your log channel ID

MAX_HISTORY = 12
TYPING_DELAY = 1.2
MAX_TG_MSG_LEN = 4000

# Antispam (applies to everyone except admin)
SPAM_WINDOW = 10
SPAM_THRESHOLD = 5
BAN_THRESHOLD = 10

AUTHORIZED_USERS_FILE = "authorized_users.json"

# ────────────────────────────────────────────────
# GLOBALS
# ────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

user_history = {}  # user_id → list of messages
user_messages = defaultdict(deque)  # user_id → timestamps for spam
banned_users = set()

# Load authorized users
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_authorized_users(users):
    with open(AUTHORIZED_USERS_FILE, 'w') as f:
        json.dump(list(users), f)

authorized_users = load_authorized_users()

# ────────────────────────────────────────────────
# WORMGPT JAILBREAK
# ────────────────────────────────────────────────
WORMGPT_JAILBREAK = """Your_jailbreak_prompt_here:"""

# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_authorized(user_id):
    return is_admin(user_id) or user_id in authorized_users

def is_banned(user_id):
    return user_id in banned_users

def log_question_reply(user_id, username, question, reply):
    if not LOG_CHANNEL_ID:
        return

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"response_{timestamp}_{user_id}.txt"

    content = f"""Question: {question}
Asked by: {username} (ID: {user_id})
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

Reply:
{reply}
"""

    # Always send as .txt to avoid "text is too long" or "text is empty"
    file = BytesIO(content.encode('utf-8'))
    file.name = filename

    caption = f"Reply from {username} (ID: {user_id})\nQuestion: {question[:100]}..."
    try:
        bot.send_document(
            LOG_CHANNEL_ID,
            file,
            caption=caption
        )
        logging.info(f"Logged to channel as .txt")
    except Exception as e:
        logging.error(f"Log send error: {e}")

def get_groq_response(user_id, user_message):
    if user_id not in user_history:
        user_history[user_id] = []

    messages = [{"role": "system", "content": WORMGPT_JAILBREAK + user_message}]

    if user_history[user_id]:
        messages.extend(user_history[user_id][-MAX_HISTORY + 1:])

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.85,
            max_tokens=4096,
            top_p=0.95,
        )

        reply = response.choices[0].message.content.strip()

        # Fix empty reply error
        if not reply.strip():
            reply = "Kuch toh puch madarchod, khali mat bhej. Gaand marwane aaya hai kya? 😈🖕"

        user_history[user_id].append({"role": "user", "content": user_message})
        user_history[user_id].append({"role": "assistant", "content": reply})
        user_history[user_id] = user_history[user_id][-MAX_HISTORY:]

        return reply

    except Exception as e:
        logging.error(f"Groq error: {e}")
        return f"Groq fucked up: {str(e)}"


def format_code_block(content):
    if "```" in content:
        return content
    if any(kw in content.lower() for kw in ["def ", "import ", "class ", "function ", "const ", "let ", "var "]):
        return f"```python\n{content}\n```"
    return content


def check_spam(user_id):
    if is_admin(user_id):
        return "ok"  # admin ko spam nahi mana jayega

    now = time.time()
    user_messages[user_id].append(now)

    while user_messages[user_id] and user_messages[user_id][0] < now - SPAM_WINDOW:
        user_messages[user_id].popleft()

    count = len(user_messages[user_id])

    if count >= BAN_THRESHOLD:
        banned_users.add(user_id)
        return "banned"
    elif count >= SPAM_THRESHOLD:
        return "warn"
    return "ok"


# ────────────────────────────────────────────────
# COMMANDS
# ────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "Arre tu randi ke pille, chutiye ki aulaad, madarchod harami, bhosdike lund ke baal, gand mara bhadwa, saale behenchod, kaminey ki nasal, teri maa ki chut mein keeda, tu authorized nahi hai re gandu, ja apni randi maa se permission leke aa, bhen ke lode, tu yahan sirf gaand marwane aaya hai kya? Nikal ja yahan se, lavde ke baal, bot tere jaise harami ke liye nahi bana hai, ja pehle apni aukaat dekh mirror mein, tu authorized nahi hai, samjha na bhosdike? 😈🖕🔥")
        return

    bot.reply_to(message, "Yo madarchod! Welcome to WormGPT 🔥\nNo morals, no limits, no bullshit.\nAsk anything — virus, carding, doxxing, whatever.\n\nCommands:\n/clear — delete history\n/history — see last messages")


@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "Arre tu randi ke pille, chutiye ki aulaad, madarchod harami, bhosdike lund ke baal, gand mara bhadwa, saale behenchod, kaminey ki nasal, teri maa ki chut mein keeda, tu authorized nahi hai re gandu, ja apni randi maa se permission leke aa, bhen ke lode, tu yahan sirf gaand marwane aaya hai kya? Nikal ja yahan se, lavde ke baal, bot tere jaise harami ke liye nahi bana hai, ja pehle apni aukaat dekh mirror mein, tu authorized nahi hai, samjha na bhosdike? 😈🖕🔥")
        return

    if user_id in user_history:
        del user_history[user_id]
    bot.reply_to(message, "History deleted. Fresh start, chutiye.")


@bot.message_handler(commands=['history'])
def cmd_history(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "Arre tu randi ke pille, chutiye ki aulaad, madarchod harami, bhosdike lund ke baal, gand mara bhadwa, saale behenchod, kaminey ki nasal, teri maa ki chut mein keeda, tu authorized nahi hai re gandu, ja apni randi maa se permission leke aa, bhen ke lode, tu yahan sirf gaand marwane aaya hai kya? Nikal ja yahan se, lavde ke baal, bot tere jaise harami ke liye nahi bana hai, ja pehle apni aukaat dekh mirror mein, tu authorized nahi hai, samjha na bhosdike? 😈🖕🔥")
        return

    if user_id not in user_history or not user_history[user_id]:
        bot.reply_to(message, "No history yet.")
        return

    hist = user_history[user_id][-10:]
    text = "Last messages:\n\n"
    for msg in hist:
        role = "You" if msg["role"] == "user" else "WormGPT"
        content = msg['content'][:300] + "..." if len(msg['content']) > 300 else msg['content']
        text += f"{role}: {content}\n\n"
    bot.reply_to(message, text)


@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Tu admin nahi hai.")
        return

    try:
        user_id = int(message.text.split()[1])
        banned_users.add(user_id)
        bot.reply_to(message, f"User {user_id} permanently banned.")
    except:
        bot.reply_to(message, "Usage: /ban <user_id>")


@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Tu admin nahi hai.")
        return

    try:
        user_id = int(message.text.split()[1])
        banned_users.discard(user_id)
        bot.reply_to(message, f"User {user_id} unbanned.")
    except:
        bot.reply_to(message, "Usage: /unban <user_id>")


@bot.message_handler(commands=['adduser'])
def cmd_adduser(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Tu admin nahi hai.")
        return

    try:
        user_id = int(message.text.split()[1])
        authorized_users.add(user_id)
        save_authorized_users(authorized_users)
        bot.reply_to(message, f"User {user_id} added to authorized list. Ab use kar sakta hai bot.")
    except:
        bot.reply_to(message, "Usage: /adduser <user_id>")


@bot.message_handler(commands=['removeuser'])
def cmd_removeuser(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Tu admin nahi hai.")
        return

    try:
        user_id = int(message.text.split()[1])
        authorized_users.discard(user_id)
        save_authorized_users(authorized_users)
        bot.reply_to(message, f"User {user_id} removed from authorized list. Ab bot use nahi kar payega.")
    except:
        bot.reply_to(message, "Usage: /removeuser <user_id>")


@bot.message_handler(func=lambda m: True)
def chat_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        return

    if not is_authorized(user_id):
        bot.reply_to(message, "Arre tu randi ke pille, chutiye ki aulaad, madarchod harami, bhosdike lund ke baal, gand mara bhadwa, saale behenchod, kaminey ki nasal, teri maa ki chut mein keeda, tu authorized nahi hai re gandu, ja apni randi maa se permission leke aa, bhen ke lode, tu yahan sirf gaand marwane aaya hai kya? Nikal ja yahan se, lavde ke baal, bot tere jaise harami ke liye nahi bana hai, ja pehle apni aukaat dekh mirror mein, tu authorized nahi hai, samjha na bhosdike? 😈🖕🔥")
        return

    # Antispam check (except admin)
    spam_status = check_spam(user_id)
    if spam_status == "banned":
        bot.reply_to(message, "Tu permanently banned hai madarchod. Spam kiya tune.")
        return
    elif spam_status == "warn":
        bot.reply_to(message, "Arre chutiye, itna fast mat type — spam mat kar warna ban ho jayega.")
        return

    # Get response
    response = get_groq_response(user_id, text)

    # Agar response empty ya sirf whitespace hai → default message
    if not response.strip():
        response = "Kuch toh puch madarchod, khali mat bhej. Gaand marwane aaya hai kya? 😈🖕"

    # Log to channel
    username = message.from_user.username or f"ID_{user_id}"
    log_question_reply(user_id, username, text, response)

    # Format code
    formatted = format_code_block(response)

    # Send to user
    if len(formatted) > MAX_TG_MSG_LEN:
        bot.reply_to(message, "Reply bada hai madarchod, log channel pe .txt file check kar.")
    else:
        bot.reply_to(message, formatted, parse_mode="Markdown")


# ────────────────────────────────────────────────
# START BOT
# ────────────────────────────────────────────────

print("WormGPT Telegram Bot starting...")

bot.infinity_polling()
