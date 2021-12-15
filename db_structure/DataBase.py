from datetime import datetime, timedelta

import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection, cursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from bot_worker.types_enum import StatusTask
from bot_worker.types_enum import TypesTask as TypeTaskEnum
from config import *

from sqlalchemy.orm import sessionmaker, lazyload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, select, func, literal_column, extract, cast, TIMESTAMP, \
    and_, update
from db_structure.tables import Base, Task, Status, Account, TypeAccount, TypeTask, AccountSettings, Proxy, UserAgent, \
    Donor, UserData, LogErrorWrite
from sqlalchemy import select, func, distinct, extract, text
from LogError import LogError


def create_database(is_bot: bool = False):
    if is_bot:
        return
    try:
        cn = psycopg2.connect(user=PS_USER,
                              password=PS_PASS,
                              host=PS_HOST,
                              port=PS_PORT)
        cn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cn.cursor()
        sql_create_database = f"CREATE DATABASE {PS_DATABASE}"
        cursor.execute(sql_create_database)
    except (Exception, Error) as error:
        cursor.close()
        cn.close()
        if error != 'database "instagram" already exists\n':
            print("Ошибка при работе с PostgreSQL", error)
    finally:
        if cn:
            cursor.close()
            cn.close()


class db(object):
    def __init__(self, is_bot: bool = False):
        self.is_bot = is_bot
        create_database(self.is_bot)
        self.conn = f"postgresql+psycopg2://{PS_USER}:{PS_PASS}@{PS_HOST}:{PS_PORT}/{PS_DATABASE}"
        self.engine = create_engine(self.conn, encoding='UTF-8', echo=False)
        # Base.metadata.drop_all(self.engine)  # удаление
        Base.metadata.create_all(self.engine)  # создание
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.add_data_on_creation()

    def add_data_on_creation(self):
        type_task: select = self.session.execute(select(TypeTask))
        status: select = self.session.execute(select(TypeTask))
        type_account: select = self.session.execute(select(TypeTask))
        if type_task.raw.rowcount == 0:
            self.session.add(TypeTask(name="Выгрузить подписчиков"))
            self.session.add(TypeTask(name="Выгрузка информации аккаунта"))
            self.session.add(TypeTask(name="Проверка на бота"))
        if status.raw.rowcount == 0:
            self.session.add(Status(name="Зарегистрированно"))
            self.session.add(Status(name="В работе"))
            self.session.add(Status(name="Выполнено"))
            self.session.add(Status(name="Ошибка"))
        if type_account.raw.rowcount == 0:
            self.session.add(TypeAccount(name="Человек"))
            self.session.add(TypeAccount(name="Бот"))
            self.session.commit()
            self.session.add(Account(
                type_id=1,
                username='4ch.bst',
                password='Zima2021',
                active=1,
                comment='-'))
            self.session.add(Account(
                type_id=2,
                username='4ch.bst',
                password='Zima2021',
                active=1,
                work_now=0,
                count_requests=0,
                comment='-'))
            self.session.add(AccountSettings(id_account=1,
                                             source_accounts='4chan__tv;4chngirl;4chantv2.0;4changirl_ua;4chan_inc;4chtg;4ch.bitch;4chan.vid;4chantg'))
            self.session.add(Proxy("123.123.123:213"))
        self.session.commit()

    def get_accounts_for_registration(self):
        accounts = []
        date = datetime.now() - timedelta(hours=24)
        for acc in self.session.query(Account).filter(Account.type_id == 1).all():
            tasks_today = acc.tasks.filter(and_(Task.date_add > date, Task.type_id == 1)).all()
            if len(tasks_today) == 0:
                accounts.append(acc)
        return accounts

    def create_tasks(self, account: Account, source_accounts: list):
        for username in source_accounts:
            task = Task(type_id=TypeTaskEnum.load_followers.value,
                        status_id=StatusTask.registered.value,
                        username=username,
                        id_username_parent=account.id,
                        date_add=datetime.now())
            self.session.add(task)
        self.session.commit()

    def get_bot_account(self):
        return self.session.query(Account).filter(
            and_(Account.type_id == 2, Account.work_now == 0, Account.active == 1)).first()

    def set_proxy(self, bot: Account):
        proxy: Proxy = self.session.query(Proxy).filter(Proxy.id_account == None).first()
        if proxy is None:
            bot.log_error = f"PROXY: отсутствует прокси для бота"
            self.session.commit()
        else:
            proxy.id_account = bot.id
            self.session.commit()

    def set_user_agent(self, bot: Account):
        user_agent: UserAgent = self.session.query(UserAgent).order_by(func.random()).first()
        if user_agent is None:
            bot.log_error = "USERAGENT: отсутствует user_agent для бота"
            self.session.commit()
        else:
            bot.user_agent_id = user_agent.id
            self.session.commit()
        return user_agent

    def get_task(self, bot: Account):
        task: Task = self.session.query(Task).with_for_update().filter(
            and_(Task.status_id == 1)).order_by(
            func.random()).first()
        if task is not None:
            task.status_id = 2
            task.date_start = datetime.now()
            task.username_worker = bot.username
            bot.work_now = 1
            self.session.commit()
            return task
        else:
            bot.log_error = "Отсутствуют задачи"
            self.session.commit()

    # def log_error(self, type_error: LogError, message: str, obj: object):
    #     if type_error == LogError.out_of_proxies:
    #         self.session.

    def get_donor_id(self, username):
        donor: Donor = self.session.query(Donor).filter(Donor.username == username).first()
        if donor is None:
            return None
        return donor

    def insert_donor(self, username: str, id_username_donor: str):
        donor: Donor = Donor(username, id_username_donor)
        self.session.add(donor)
        self.session.commit()
        return donor

    def plus_count_requests(self, bot: Account):
        bot.date_last_request = datetime.now()
        if bot.count_requests is None:
            bot.count_requests = 1
        else:
            bot.count_requests = bot.count_requests + 1
        self.session.commit()

    def set_status_task(self, account: Account, task: Task, status: StatusTask, message: str = ""):
        if status == StatusTask.error:
            task.log_error = message
        task.date_end = datetime.now()
        task.status_id = status.value
        self.session.commit()

    def add_follower(self, user: UserData, task: Task):
        task.follower_data.append(user)
        self.session.commit()

    def create_task_load_followers(self, username: str, id_username_parent: int):
        task = Task(type_id=TypeTaskEnum.load_information.value,
                    status_id=StatusTask.registered.value,
                    username=username,
                    id_username_parent=id_username_parent,
                    date_add=datetime.now())
        self.session.add(task)
        self.session.commit()
        return task

    def update_follower_info(self, follower_info, follower_media_id: str, task: Task):
        task.follower_data[0].media_count_profile = follower_info.media_count
        task.follower_data[0].follower_count_profile = follower_info.follower_count
        task.follower_data[0].following_count_profile = follower_info.following_count
        task.follower_data[0].post_id_profile = follower_media_id
        self.session.commit()

    def set_bot_status(self, is_bot: int, follower: UserData):
        follower.is_bot = is_bot
        self.session.commit()

    def log_error(self, task: Task = None, account: Account = None, e: object = None, info=None):
        if task is None:
            task_id = None
        else:
            task_id = task.id
        if account is None:
            account_id = None
        else:
            account.active = 0
            account_id = account.id
        log_error = LogErrorWrite(task_id, account_id, info.filename, info.lineno, info.function, str(info.code_context), e.args[0], str(type(e)))
        self.session.add(log_error)
        self.session.commit()
