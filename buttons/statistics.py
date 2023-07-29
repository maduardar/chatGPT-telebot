from telegram import Update
from telegram.ext import ContextTypes
from db.MySqlConn import Mysql
from config import (
    reply_markup,
    CHOOSING)


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    mysql = Mysql()
    user_id = user.id
    prompt_tokens = mysql.getMany(
        f"select sum(tokens) as tokens from records where user_id={user_id} and role='user'", 1)[0]
    completion_tokens = mysql.getMany(
        f"select sum(tokens) as tokens from records where user_id={user_id} and role='assistant'", 1)[0]

    if not prompt_tokens["tokens"]:
        prompt_tokens["tokens"] = 0
    if not completion_tokens["tokens"]:
        completion_tokens["tokens"] = 0

    await update.message.reply_html(
        rf"""
Привет,  {user.mention_html()}!

Вот сколько токенов ты потратил:
На запрос：{prompt_tokens["tokens"]} токенов
На ответ：{completion_tokens["tokens"]} токенов
Итого：{prompt_tokens["tokens"] + completion_tokens["tokens"]} токенов

 """,
        reply_markup=reply_markup, disable_web_page_preview=True
    )
    return CHOOSING
