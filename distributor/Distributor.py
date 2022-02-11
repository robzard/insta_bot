from db_structure.tables import *
import docker
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


class Distributor:
    def __init__(self, db_connection):
        self.db = db_connection
        self.client = docker.from_env()

    def registration_tasks(self):
        accounts = self.db.get_accounts_for_registration()
        for row in accounts:
            acc: Account = row
            source_accounts = acc.account_settings.source_accounts.split(';')
            self.db.create_tasks(acc, source_accounts)

    def docker_run_containers(self):
        self.docker_build_image()
        containers_running_count = len(self.client.containers.list(filters={'status': 'exited'}).count())
        count_tasks = self.db.get_count_tasks()
        need_containers = round(count_tasks / 150) - containers_running_count
        if need_containers > 0:
            for i in range(0, need_containers):
                self.client.containers.run('bot_worker', detach=True)

    def docker_build_image(self):
        images = ''
        images_list = [images + str(el) for el in self.client.images.list()]
        if 'bot_worker' not in str(images_list):
            self.client.images.build(path=ROOT_DIR,
                                     tag='bot_worker')
