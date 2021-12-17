import sys
import traceback
import requests
from instagrapi.exceptions import ClientLoginRequired
from ExceptionsInst import InstBotException
from bot_worker.InstagramBot import InstagramBot
from bot_worker.types_enum import StatusTask
from db_structure import DataBase
from db_structure.DataBase import db
import inspect
from db_structure.tables import Account


if __name__ == '__main__':
    print('Start')
    db_ps = db(True)
    bot = InstagramBot(db_ps)
    try:
        if bot.get_bot_instagram():
            bot.tasks_working()
            print('q')
    except InstBotException:
        pass
    except Exception as e:
        traceback.print_exc()
        info = inspect.trace()[-1]
        print(f"Возникла корневая ошибка: {info}")
        db_ps.log_error(bot.task, bot.bot, e, info)
    finally:
        if bot.bot is not None:
            bot.bot.work_now = 0
            bot.db.session.commit()
    print('End')
