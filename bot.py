import os
import sqlite3
import requests
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import google.generativeai as genai

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PAY_URL = os.getenv("PAY_URL")  # لینک درگاه پرداخت

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro",)

# ================= DATABASE =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
vip_until TEXT
)
""")
conn.commit()

# ================= MENU =================
menu = ReplyKeyboardMarkup([
    ["🤖 AI"],
    ["💰 طلا", "💵 دلار"],
    ["⭐ خرید VIP"],
    ["👤 حساب کاربری"],
    ["ℹ️ درباره"]
], resize_keyboard=True)

# ================= DB =================
def add_user(uid):
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (uid, None))
    conn.commit()

def set_vip(uid, days=30):
    vip_time = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("UPDATE users SET vip_until=? WHERE user_id=?", (vip_time, uid))
    conn.commit()

def is_vip(uid):
    c.execute("SELECT vip_until FROM users WHERE user_id=?", (uid,))
    r = c.fetchone()
    if not r or not r[0]:
        return False
    return datetime.fromisoformat(r[0]) > datetime.now()

def count_users():
    c.execute("SELECT COUNT(*) FROM users")
    return c.fetchone()[0]

# ================= API =================
def gold():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json").json()
        return f"💰 طلا: {r['data']['geram18']['p']} تومان"
    except:
        return "❌ خطا"

def dollar():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json").json()
        return f"💵 دلار: {r['data']['usd']['p']} تومان"
    except:
        return "❌ خطا"

def ai(text):
    res = model.generate_content(text)
    return res.text

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    add_user(uid)

    await update.message.reply_text(
        "👑 ربات تجاری فعال شد\n👨‍💻 امیر علی فروزان اصل",
        reply_markup=menu
    )

# ================= HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id

    add_user(uid)

    if text == "💰 طلا":
        await update.message.reply_text(gold())
        return

    if text == "💵 دلار":
        await update.message.reply_text(dollar())
        return

    # ================= VIP =================
    if text == "⭐ خرید VIP":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 پرداخت", url=PAY_URL)]
        ])
        await update.message.reply_text("💎 خرید VIP:", reply_markup=keyboard)
        return

    # ================= AI =================
    if text == "🤖 AI":
        if not is_vip(uid) and uid != ADMIN_ID:
            await update.message.reply_text("🔒 فقط VIP")
            return
        await update.message.reply_text("✍️ پیام بده")
        return

    # AI RESPONSE
    try:
        if is_vip(uid) or uid == ADMIN_ID:
            await update.message.reply_text(ai(text))
        else:
            await update.message.reply_text("🔒 برای AI باید VIP بخری")
    except:
        await update.message.reply_text("❌ خطا")

# ================= ADMIN =================
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    uid = int(context.args[0])
    set_vip(uid, 30)
    await update.message.reply_text("✅ VIP فعال شد")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"👥 کاربران: {count_users()}")

# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
