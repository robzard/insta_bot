from bot_worker.InstagramBot import InstagramBot
from db_structure.DataBase import db


if __name__ == '__main__':
    db_ps = db(True)
    bot = InstagramBot(db_ps)
    bot.inst_login()
    task = bot.get_next_task()
    bot.task_processing()