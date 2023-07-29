from telegram import Update
from telegram.ext import ContextTypes
import time

from config import (
    reply_markup,
    CHOOSING)
from db.MySqlConn import Mysql


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("start")
    mysql = Mysql()
    user = update.effective_user
    user_id = user.id

    user_checkin = mysql.getOne(f"select * from users where user_id={user_id}")
    if not user_checkin:
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into users (user_id, name, level, system_content, created_at) values (%s, %s, %s, %s, %s)"
        value = [user_id, user.username, 0, "You are an AI assistant that helps people find information.", date_time]
        mysql.insertOne(sql, value)
    mysql.end()

    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"""
        Hey  {user.mention_html()}!
I'm an AI chatbot created to interact with you and make your day a little brighter. 
If you have any questions or just want to have a friendly chat, I'm here to help! 🤗

Do you know what's great about me? I can help you with anything from giving advice to telling you a joke.
Almost like Darina but even better as I answer almost immediately and I'm available 24/7! 🕰️
________________________________________
Привет {user.mention_html()}!
Я чат-бот, созданный для общения с тобой и того, чтобы сделать твой день немного ярче.
Если у тебя есть вопросы или ты просто хочешь поболтать, я здесь, чтобы помочь! 🤗

Знаешь, что во мне здорово? Я могу помочь тебе с чем угодно, от совета до шутки.
Почти как Дарина, но даже лучше, потому что я отвечаю почти мгновенно и доступен 24/7! 🕰️
        """,
        reply_markup=reply_markup, disable_web_page_preview=True
    )
    return CHOOSING
