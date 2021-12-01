import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection, cursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import *

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, select
from db_structure.tables import Base, Task, Status, Account, TypeAccount, TypeTask, AccountSettings


def create_database():
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
    def __init__(self):
        create_database()
        self.conn = f"postgresql+psycopg2://{PS_USER}:{PS_PASS}@{PS_HOST}:{PS_PORT}/{PS_DATABASE}"
        self.engine = create_engine(self.conn, encoding='UTF-8', echo=False)
        Base.metadata.drop_all(self.engine)  # удаление
        Base.metadata.create_all(self.engine)  # создание
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.add_data_on_creation()

        #a = self.session.query(Account).filter(Account.username.like('%4%')).all()
        print("1")
        # data: Account = self.session.query(Account).first()
        # print(data.settings.source_accounts)
        # for acc in data.scalars().all():
        #     print(acc.settings.source_accounts)

    def add_data_on_creation(self):
        type_task: select = self.session.execute(select(TypeTask))
        status: select = self.session.execute(select(TypeTask))
        type_account: select = self.session.execute(select(TypeTask))
        if type_task.raw.rowcount == 0:
            self.session.add(TypeTask(name="Выгрузить подписчиков"))
            self.session.add(TypeTask(name="Проверка на бота"))
            self.session.add(TypeTask(name="Выгрузка информации аккаунта"))
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
                    proxy='-',
                    user_agent='-',
                    active=1,
                    comment='-'))
            self.session.add(AccountSettings(id_account=1,
                                             source_accounts='4chan__tv;4chngirl;4chantv2.0;4changirl_ua;4chan_inc;4chtg;4ch.bitch;4chan.vid;4chantg'))
        self.session.commit()


    def get_accounts_for_registration(self):
        return self.session.query(Account)  # .filter(Account.username.like('4'))

    def create_tasks(self, account: Account, source_accounts: list):
        for username in source_accounts:
            task = Task(type_id=1,
                        status_id=1,
                        username=username,
                        id_username_parent=account.id,)
            self.session.add(task)
        self.session.commit()



