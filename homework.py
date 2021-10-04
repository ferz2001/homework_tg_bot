import os
import time
import logging
import requests
import telegram as tg
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(name)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
handler = RotatingFileHandler('mylog.log', maxBytes=50000000, backupCount=1)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

bot = tg.Bot(token=TELEGRAM_TOKEN)
logger.debug('Bot is ready')


def parse_homework_status(homework):
    current_status = ('rejected', 'reviewing', 'approved', 'denied')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name in (None, '') or homework_status not in current_status:
        logger.error(
            (f'Переменная homework_name - {homework_name}, '
             f'переменная homework_status - {homework_status}, '
             f'ошибка в переменной!!!'),
            exc_info=True
        )
        return 'Неверный ответ сервера'
    elif homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == 'reviewing':
        verdict = 'Работа взята в ревью. Ждите вердикта!'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        response = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        send_message(f'Бот упал с ошибкой: {e}')
        logger.error(e, exc_info=True)
        return {'Ошибка сервера, при получении данных из API'}
    homework = response.json()
    return homework


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    last_homework = None
    while True:
        try:
            current_timestamp = int(time.time() - 200000)
            homework = get_homeworks(current_timestamp)
            if homework.get('homeworks') and homework != last_homework:
                message = parse_homework_status(homework.get('homeworks')[0])
                send_message(message)
                logger.info('Message sent')
                last_homework = homework
            time.sleep(20 * 60)
        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logger.error(e, exc_info=True)
            time.sleep(30)


if __name__ == '__main__':
    main()
