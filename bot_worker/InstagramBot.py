from db_structure.tables import *


class InstagramBot:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_bot_instagram(self):

        

    def get_next_task(self):
        task: Task = self.db.get_task()