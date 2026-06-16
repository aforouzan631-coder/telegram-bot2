import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# ========== TOKENS ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# ========== KEYBOARD ==========
menu = ReplyKeyboardMarkup([
    ["🤖 هوش مصنوعی"],
    ["💰 قیمت طلا"],
    ["💵 قیمت دلار"],
    ["⭐ خرید اشتراک"],
    ["ℹ️ درباره ما"]
], resize_keyboard=True)

# ========== GOLD ==========
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/v1/data/price?key=geram18")
        data = r.json()
        return f"💰 قیمت طلا: {data['data']['price']} تومان"
    except:
        return "❌ خطا در دریافت قیمت"

# ========== AI ==========
def ai(text):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=text
    )
    return response.text

# ========== START ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 به ربات VIP خوش آمدید\n👨‍💻 سازنده: امیر علی فروزان اصل",
        reply_markup=menu
    )

# ========== MESSAGE ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "طلا" in text:
        await update.message.reply_text(gold_price())

    elif "دلار" in text:
        await update.message.reply_text("💵 در حال اتصال به API...")

    elif "هوش" in text:
        result = ai(text)
        await update.message.reply_text(result)

    elif "خرید" in text:
        await update.message.reply_text("💳 پرداخت در حال آماده سازی است...")

    else:
        await update.message.reply_text("❓ دستور نامشخص")

# ========== MAIN ==========
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
