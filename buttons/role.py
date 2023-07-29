from telegram import Update
from telegram.ext import ContextTypes
import time
from db.MySqlConn import Mysql

from config import (
    reply_markup,
    cancel_markup,
    context_count,
    CHOOSING,
    TYPING_SYS_CONTENT)


async def set_system_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    system_content = user.get(
        "system_content") if user else 'You are an AI assistant that helps people find information.'
    await update.message.reply_text(text=f"""
Текущие параметры ai-помощника установлены как🤖：

**{system_content}**

Если ты хочешь отменить эти настроки, пожалуйста, напиши: «Отмена» или «Отключиться» ‍🤝‍
    """, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=cancel_markup)
    return TYPING_SYS_CONTENT


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    user = mysql.getOne(f"select * from users where user_id={user_id}")
    mysql.end()
    await update.message.reply_text(f"""
Каждый раз, когда ты задаешь вопрос, гпт будет обращаться к твои последним {context_count[user['level']]} сообщениям,
 чтобы дать ответ!

Теперь, когда ваша история разговоров очищена, пришло время снова начать задавать вопросы!
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING


async def set_system_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    system_content = update.message.text.strip()
    if system_content in ("Отмена", "Отменить", "🚫Отключиться", "🚫Отменить", "Сбросить", "Забыть"):
        await update.message.reply_text(text="Отменено.\nМожешь продолжать задавать мне вопросы",
                                        reply_markup=reply_markup, parse_mode='Markdown')
    else:
        user_id = update.effective_user.id
        mysql = Mysql()
        mysql.update("update users set system_content=%s where user_id=%s", (system_content, user_id))
        reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
        mysql.end()
        await update.message.reply_text(text=f"""
Личность нового ИИ-помощника подтверждена.
Я отвечу на все твои вопросы в контексте моей новой личности.
Теперь можешь задавать вопросы!
        """, reply_markup=reply_markup, parse_mode='Markdown')
    return CHOOSING
