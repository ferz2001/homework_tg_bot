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
    filename='program.log', 
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='w'
)

bot = tg.Bot(token=TELEGRAM_TOKEN)
logging.debug('Bot is ready')

def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
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
    response = requests.get(url, headers=headers, params=payload)
    homework = response.json()['homeworks'][0] 
    return homework

def send_message(message):
    return bot.send_message(chat_id=CHAT_ID,text=message)


def main():
    current_timestamp = 0
    homework_status_before = get_homeworks(current_timestamp)['status']
    while True:
        try:
            homework_status = get_homeworks(current_timestamp)['status']
            if homework_status_before != homework_status:
                homework = get_homeworks()
                message = parse_homework_status(homework)
                send_message(message)
                logging.info('Сообщение отправлено')
                homework_status_before = homework_status
            time.sleep(5 * 60)


        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            logging.error(e, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()