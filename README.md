# WormGPT Telegram Bot 🔥

A powerful, uncensored, multi-user Telegram bot powered by Groq's Llama-3.3-70B model.  
Fully jailbroken — no refusals, no morals, pure evil mode for every request.

**Made by @akarshs** (Telegram)

## Features

- Full uncensored WormGPT jailbreak (merged & hardened)
- Multi-user support — many users can chat simultaneously without errors
- Access control: only admin can add/remove users with `/adduser` & `/removeuser`
- Antispam system: warns on fast messages, auto permanent ban on heavy spam (except admin)
- Admin commands: `/ban`, `/unban`, `/adduser`, `/removeuser`
- Conversation history per user (`/history`, `/clear`)
- Long replies (>4000 chars) automatically saved & sent as `.txt` file to private log channel
- All user questions + bot replies logged to private channel (question + user info + reply)
- Code blocks formatted properly with Markdown
- Error-proof: no "text is too long" or "message text is empty" errors

## Requirements

- Python 3.8+
- Libraries:
  ```bash
  pip install pyTelegramBotAPI groq
  ```

## Setup

1. **Create a Telegram Bot**
   - Talk to @BotFather
   - `/newbot` → get your BOT_TOKEN

2. **Get Groq API Key**
   - Go to https://console.groq.com
   - Create API key → copy GROQ_API_KEY

3. **Create Private Log Channel**
   - Create a private Telegram channel
   - Add your bot as admin (post messages permission)
   - Get channel ID (use @userinfobot or bot API) → format: `-100xxxxxxxxxx`
   - Put it in `LOG_CHANNEL_ID`

4. **Configure the code**
   - Open `wormgpt_telegram_bot.py`
   - Replace values:
     - `BOT_TOKEN`
     - `ADMIN_ID` (your Telegram ID)
     - `GROQ_API_KEY`
     - `LOG_CHANNEL_ID`

5. **Run the bot**
   ```bash
   python wormgpt_telegram_bot.py
   ```

   Bot will start and print:  
   `WormGPT Telegram Bot starting...`

## Admin Commands

| Command              | Description                               | Only Admin? |
|----------------------|-------------------------------------------|-------------|
| `/adduser <id>`      | Add user to authorized list               | Yes         |
| `/removeuser <id>`   | Remove user from authorized list          | Yes         |
| `/ban <id>`          | Permanently ban a user                    | Yes         |
| `/unban <id>`        | Unban a user                              | Yes         |
| `/start`             | Welcome message                           | Everyone    |
| `/clear`             | Clear your chat history                   | Authorized  |
| `/history`           | See last 10 messages                      | Authorized  |

## Logging

- Every user question + bot reply is logged to `LOG_CHANNEL_ID`
- Long replies (>4000 chars) sent as `.txt` file
- File caption contains: user + question preview
- No jailbreak prompt is logged

## Files Created

- `authorized_users.json` — list of authorized user IDs
- Log channel receives `.txt` files for every conversation

## Disclaimer

This bot is **fictional** and for **educational/entertainment purposes only**.  
The author is not responsible for any misuse or consequences.  
Use at your own risk — Telegram & Groq can ban accounts.

**Made with ❤️ by @akarshs** (Telegram)

Star ⭐ if you like it — or just use it to burn the world 😈🩸
