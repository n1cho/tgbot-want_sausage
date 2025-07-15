import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from db import (
    init_db, get_last_used_time, 
    update_last_used_time, update_sausage_stats,
    get_statistics
)
from datetime import datetime, timedelta

SAUSAGE_TYPES = [
    "варенной", "копченой", "докторской", "охотничей"
]
COOLDOWN = timedelta(minutes=2)

# Load config
with open("config.json","r",encoding="utf-8") as l:
    config = json.load(l)

BOT_TOKEN = config["bot_token"]

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Привет {update.effective_user.first_name}! Хочешь колбаски?")

# Command /kolbasa
async def kolbasa(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    now = datetime.now()

    last_used = get_last_used_time(chat.id, user.id)
    if last_used and now-last_used < COOLDOWN:
        remaining = COOLDOWN - (now - last_used)
        total_seconds = int(remaining.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        await update.message.reply_text(f"Куда тебе столько! Ты уже свою порцию съел, попробуй снова через {hours:02d}:{minutes:02d}:{seconds:02d}.")
        return
    
    sausage = random.choice(SAUSAGE_TYPES)
    quantity = round(random.uniform(0.1, 1.0), 2)

    update_sausage_stats(chat.id, user.id, user.first_name, sausage, quantity)
    update_last_used_time(chat.id, user.id, now)

    await update.message.reply_text(
        f"{user.first_name} съел {quantity} кг *{sausage}* колбасы", parse_mode="Markdown"
    )
    
# Comand /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    stats = get_statistics(chat.id)

    if not stats:
        await update.message.reply_text("В этом чате ещё никто не кушал(")
        return
    
    message = "Стастистика чата по употреблению колбасы:\n"
    for user, user_data in stats.items():
        total = round(sum(user_data.values()), 2)
        parts = [f"{k}: {v}" for k, v in user_data.items()]
        message += f"👤 {user}: {total} кг ({', '.join(parts)})\n"

    await update.message.reply_text(message, parse_mode="Markdown")

# Start bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kolbasa",kolbasa))
    app.add_handler(CommandHandler("stats", stats))

    app.run_polling()

if __name__ == "__main__":
    init_db()
    main()