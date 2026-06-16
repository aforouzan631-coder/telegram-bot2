import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

# ====== TOKENS ======
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# ====== KEYBOARD ======
menu = ReplyKeyboardMarkup([
    ["🤖 هوش مصنوعی"],
    ["💰 قیمت طلا"],
    ["💲 قیمت دلار"],
    ["ℹ️ درباره ما"]
], resize_keyboard=True)

# ====== GOLD ======
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json")
        data = r.json()
        return f"💰 طلا: {data['data']['gold18']['p']}"
    except:
        return "❌ خطا در دریافت قیمت"

# ====== AI ======
def ai(text):
    res = client.models.generate_content(
        model="gemini-1.5-flash-latest"
        contents=text
    )
    return res.text

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 سازنده: امیر علی فروزان اصل\n📢 @amirforozanasl",
        reply_markup=menu
    )

# ====== MESSAGE ======
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 قیمت طلا":
        await update.message.reply_text(gold_price())

    elif text == "💲 قیمت دلار":
        await update.message.reply_text("در حال توسعه 💲")

    elif text == "🤖 هوش مصنوعی":
        await update.message.reply_text(ai("سلام!"))

    else:
        await update.message.reply_text(ai(text))

# ====== MAIN ======
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
