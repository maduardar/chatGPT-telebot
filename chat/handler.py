from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import asyncio
import tiktoken
import re

from chat.ai import ChatCompletionsAI
import time
import emoji
from db.MySqlConn import Mysql

from config import (
    token,
    reply_markup,
    CHOOSING,
    rate_limit,
    time_span,
    context_count)


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    prompt = update.message.text
    user_id = user.id
    mysql = Mysql()

    user_checkin = mysql.getOne(f"select * from users where user_id={user_id}")
    if not user_checkin:
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into users (user_id, name, level, system_content, created_at) values (%s, %s, %s, %s, %s)"
        value = [user_id, user.username, 0, "You are an AI assistant that helps people find information.", date_time]
        mysql.insertOne(sql, value)
    logged_in_user = mysql.getOne(f"select * from users where user_id={user_id}")
    print(logged_in_user)
    parse_mode = logged_in_user.get("parse_mode")
    # VIP level
    level = logged_in_user.get("level")

    # Rate limit controller
    chat_count = mysql.getOne(
        f"select count(*) as count from records where role='user' and created_at >=NOW() - INTERVAL {time_span} MINUTE;")

    if chat_count.get("count") > rate_limit[level]:
        reply = f"Не так быстро!{emoji.emojize(':rocket:')}\n" \
                f"Каждые {time_span} минуты ты можешь задавать мне до  {rate_limit[level]} вопросов {emoji.emojize(':weary_face:')}\n" \
                f"Свяжись с @drnMDR для получения дополнительной помощи!{emoji.emojize(':check_mark_button:')}\n" \
                f"Или повтори попытку позже！"
        await update.message.reply_text(reply, reply_markup=reply_markup)
        return CHOOSING

    placeholder_message = await update.message.reply_text("...")
    # Init messages
    records = mysql.getMany(f"select * from records where user_id={user_id} and reset_at is null order by id desc",
                            context_count[level])
    if update.message:
        messages = []
        prompt_tokens = 0
        if records:
            for record in records:
                messages.append({"role": record["role"], "content": record["content"]})
                prompt_tokens += count_tokens(record["content"])
            messages.reverse()
        messages.insert(0, {"role": "system", "content": logged_in_user["system_content"]})
        prompt_tokens += count_tokens(logged_in_user["system_content"])
        messages.append({"role": "user", "content": prompt})
        prompt_tokens += count_tokens(prompt)

        replies = ChatCompletionsAI(logged_in_user, messages)
        prev_answer = ""
        index = 0
        async for reply in replies:
            index += 1
            answer, status = reply
            if abs(count_tokens(answer) - count_tokens(prev_answer)) < 30 and status is None:
                continue
            prev_answer = answer
            try:
                if status == "length":
                    answer = f"{answer}\n\nОтвет слышком длинный. Свяжись с @drnMDR для получения дополнительной помощи!" \
                             f"{emoji.emojize(':check_mark_button:')}"
                # elif status == "content_filter":
                #     answer = f"{answer}\n\n作为一名AI助手，请向我提问合适的问题！\n请联系 @AiMessagerBot 获取更多帮助!" \
                #              f"{emoji.emojize(':check_mark_button:')}"
                await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                    message_id=placeholder_message.message_id,
                                                    parse_mode=parse_mode)
            except BadRequest as e:
                if str(e).startswith("Message is not modified"):
                    continue
                else:
                    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                        message_id=placeholder_message.message_id)
            await asyncio.sleep(0.01)  # wait a bit to avoid flooding

        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into records (user_id, role, content, created_at, tokens) " \
              "values (%s, %s, %s, %s, %s)"
        value = [user_id, "user", prompt, date_time, prompt_tokens]
        mysql.insertOne(sql, value)

        # date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = [user_id, 'assistant', answer, date_time, count_tokens(answer)]
        mysql.insertOne(sql, value)
        mysql.end()
    return CHOOSING


def count_tokens(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

    return token_count
