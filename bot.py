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
    ["⭐ خرید اشتراک"],
    ["📞 ارتباط عمومی"],
    ["ℹ️ درباره ما"]
], resize_keyboard=True)

CREATOR = "👨‍💻 امیر علی فروزان اصل"
CONTACT = "@amirforozanasl"

def gold():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json").json()
        return f"💰 طلا: {r['data']['geram18']} تومان"
    except:
        return "❌ خطا"

def ai(text):
    res = client.models.generate_content(
        model="gemini-1.5-flash-latest"
        contents=text
    )
    return res.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 خوش آمدید\n{CREATOR}\n{CONTACT}",
        reply_markup=menu
    )

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 قیمت طلا":
        await update.message.reply_text(gold())
        return

    if text == "📞 ارتباط عمومی":
        await update.message.reply_text(CONTACT)
        return

    if text == "ℹ️ درباره ما":
        await update.message.reply_text(f"{CREATOR}\n{CONTACT}")
        return

    if text == "⭐ خرید اشتراک":
        await update.message.reply_text(
            "💳 خرید اشتراک\n\n🔗 اینجا لینک درگاه را بعداً می‌گذاری"
        )
        return

    try:
        reply = ai(text)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
