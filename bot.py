import os
import sqlite3
import requests
from datetime import datetime, timedelta

from flask import Flask, request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import google.generativeai as genai

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ZARINPAL_MERCHANT = os.getenv("ZARINPAL_MERCHANT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BASE_URL = os.getenv("BASE_URL")  # لینک Railway

bot = Bot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

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

# ================= VIP =================
def give_vip(user_id, days=30):
    vip_time = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("UPDATE users SET vip_until=? WHERE user_id=?", (vip_time, user_id))
    conn.commit()

def is_vip(user_id):
    c.execute("SELECT vip_until FROM users WHERE user_id=?", (user_id,))
    r = c.fetchone()
    if not r or not r[0]:
        return False
    return datetime.fromisoformat(r[0]) > datetime.now()

# ================= PAYMENT =================
def create_payment(user_id):
    data = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": 50000,
        "callback_url": f"{BASE_URL}/verify?user_id={user_id}",
        "description": "VIP Subscription"
    }

    res = requests.post(
        "https://api.zarinpal.com/pg/v4/payment/request.json",
        json=data
    ).json()

    return res

# ================= AI =================
def ai(text):
    res = model.generate_content(text)
    return res.text

# ================= TRANSLATE =================
def translate(text):
    res = model.generate_content(f"Translate to English: {text}")
    return res.text

# ================= MENU =================
menu = ReplyKeyboardMarkup([
    ["🤖 AI"],
    ["🌍 مترجم"],
    ["💰 طلا", "💵 دلار"],
    ["💎 خرید VIP"]
], resize_keyboard=True)

# ================= START =================
async def start(update, context):
    await update.message.reply_text("👑 ربات VIP فعال شد", reply_markup=menu)

# ================= HANDLE =================
async def handle(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "💎 خرید VIP":
        pay = create_payment(user_id)

        if pay.get("data"):
            link = "https://www.zarinpal.com/pg/StartPay/" + pay["data"]["authority"]
            await update.message.reply_text(f"💳 پرداخت:\n{link}")
        else:
            await update.message.reply_text("❌ خطا در پرداخت")
        return

    if text == "🤖 AI":
        if not is_vip(user_id):
            await update.message.reply_text("🔒 فقط VIP")
            return
        await update.message.reply_text(ai("سلام"))
        return

    if text == "🌍 مترجم":
        await update.message.reply_text(translate(text))
        return

    await update.message.reply_text("❓ دستور نامشخص")

# ================= FLASK VERIFY =================
app = Flask(__name__)

@app.route("/verify")
def verify():
    authority = request.args.get("Authority")
    user_id = int(request.args.get("user_id"))

    data = {
        "merchant_id": ZARINPAL_MERCHANT,
        "authority": authority,
        "amount": 50000
    }

    res = requests.post(
        "https://api.zarinpal.com/pg/v4/payment/verify.json",
        json=data
    ).json()

    if res.get("data", {}).get("code") == 100:
        give_vip(user_id, 30)
        bot.send_message(user_id, "✅ VIP شما فعال شد 👑")
        return "OK"

    return "FAILED"

# ================= RUN =================
app_bot = Application.builder().token(BOT_TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
