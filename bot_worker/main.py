import traceback

import requests
from instagrapi.exceptions import ClientLoginRequired

from bot_worker.InstagramBot import InstagramBot
from db_structure.DataBase import db
import inspect

if __name__ == '__main__':
    print('Start')
    try:
        db_ps = db(True)
        bot = InstagramBot(db_ps)
        if bot.get_bot_instagram():
            while bot.bot.count_requests < 200:
                if bot.get_next_task(3):
                    bot.inst_login()
                    bot.task_processing()
                else:
                    break
                print('-' * 10)
    except Exception as e:
        traceback.print_exc()
        info = inspect.trace()[-1]
        print(f"Возникла ошибка: {info}")
        db_ps.log_error(bot.task, bot.bot, e, info)
    except requests.exceptions.TooManyRedirects:
        print('Exceeded 30 redirects')

    finally:
        if bot.bot is not None:
            bot.bot.work_now = 0
    print('End')