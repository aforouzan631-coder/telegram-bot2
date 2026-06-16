import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

menu = ReplyKeyboardMarkup([
    ["🤖 هوش مصنوعی"],
    ["💰 قیمت طلا"],
    ["💵 قیمت دلار"],
    ["ℹ️ درباره ما"]
], resize_keyboard=True)


# ===== AI =====
def ai(text):
    res = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=text
    )
    return res.text


# ===== GOLD =====
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/api/v1/data/sana/json")
        data = r.json()

        gold = data['data']['gold18']
        return f"💰 طلای 18 عیار: {gold}"

    except:
        return "❌ خطا در دریافت قیمت"


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 سازنده: امیر علی فروزان اصل\n@amirforozanasl",
        reply_markup=menu
    )


# ===== MESSAGE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 قیمت طلا":
        await update.message.reply_text(gold_price())

    elif text == "🤖 هوش مصنوعی":
        await update.message.reply_text(ai("سلام"))

    else:
        await update.message.reply_text(ai(text))


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
