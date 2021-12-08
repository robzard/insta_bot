from db_structure.tables import *


class InstagramBot:
    def __init__(self, db_connection):
        self.db = db_connection
        self.bot: Account = self.get_bot_instagram()
        self.check_data_account()

    def get_bot_instagram(self):  # need work
        bot: Account = self.db.get_bot_account()
        return bot

    def check_data_account(self):
        if self.bot.proxy is None:
            self.db.set_proxy(self.bot)
        if self.bot.user_agent is None:
            self.db.set_user_agent(self.bot)

    def get_next_task(self):
        task: Task = self.db.get_task()
        return task
