from telegram import ReplyKeyboardMarkup
import logging
import yaml

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

fh = logging.FileHandler('main.log')

formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fh)

# Load data from config.yaml file
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
time_span = config["TIME_SPAN"]
token = config["MAX_TOKEN"]
context_count = config["CONTEXT_COUNT"]
rate_limit = config["RATE_LIMIT"]
open_ai_version = config["AI"]["VERSION"]
CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT = range(3)
contact_admin = "🆘Памагити"
start_button = "🚀Start"
set_sys_content_button = "🆔Задать роль для ИИ"
reset_context_button = "🔃Сбросить историю"
statistics_button = "📈Статистика"
switch_role_button = "🙋Выбрать из готовых ролей"
reply_keyboard = [
    [contact_admin, start_button],
    [set_sys_content_button, switch_role_button],
    [reset_context_button, statistics_button],
]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

cancel_button = "🚫Отменить"
cancel_keyboard = [[cancel_button]]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True)
