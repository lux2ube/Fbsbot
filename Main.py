import json
from telegram import Update, Message, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import threading
from flask import Flask

# === ضع توكن البوت هنا ===
BOT_TOKEN = "7701190517:AAHR4nJDg1B6YpVzNdiprh7jQlmq6PTv84A"

# === رقم مجموعة الإدارة ===
GROUP_ID = -1002700770095

# === تحميل رسائل البوت من ملف JSON ===
with open("messages.json", "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

# === تخزين معرفات المستخدمين والرسائل المعاد توجيهها للمجموعة (لربط الردود) ===
forwarded_messages = {}  # { forwarded_message_id_in_group: user_id }

# --- أوامر البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES["start_message"], parse_mode="HTML")
    forwarded = await update.message.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

async def open_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES["open_account"], parse_mode="HTML", disable_web_page_preview=True)
    forwarded = await update.message.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

async def link_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES["link_account"], parse_mode="HTML")
    forwarded = await update.message.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES["add_account"], parse_mode="HTML")
    forwarded = await update.message.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES["help"], parse_mode="HTML")
    forwarded = await update.message.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

# --- إعادة توجيه كل رسالة خاصة للمجموعة مع حفظ المرسل ---
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    forwarded = await msg.forward(chat_id=GROUP_ID)
    forwarded_messages[forwarded.message_id] = update.effective_user.id

# --- الردود من المجموعة تُرسل للخاص ---
async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.reply_to_message and msg.reply_to_message.message_id in forwarded_messages:
        original_user_id = forwarded_messages[msg.reply_to_message.message_id]
        try:
            await context.bot.send_message(chat_id=original_user_id, text=msg.text)
        except Exception as e:
            print(f"خطأ في إرسال الرد للمستخدم: {e}")

# --- Flask app لإبقاء السيرفر شغال ---
flask_app = Flask("keep_alive")

@flask_app.route("/")
def home():
    return "بوت تيليجرام يعمل ✅"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# --- تشغيل البوت ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # تشغيل Flask في خلفية مستقلة

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("open_account", open_account))
    app.add_handler(CommandHandler("link_account", link_account))
    app.add_handler(CommandHandler("add_account", add_account))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.ALL, handle_private_message))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.REPLY, handle_group_reply))

    print("🤖 البوت يعمل الآن...")
    app.run_polling()
