import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection, cursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import *

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, select
from db_structure.tables import Base, Task, Status, Account, TypeAccount, TypeTask


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
        self.engine = create_engine(self.conn, encoding='UTF-8',
                                    echo=False)
        # Удалить таблицу данных отображения (если она существует)
        Base.metadata.drop_all(self.engine)
        # Создать таблицу данных отображения (если она не существует)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.add_data_on_creation()

    def add_data_on_creation(self):
        type_task: select = self.session.execute(select(TypeTask))
        status: select = self.session.execute(select(TypeTask))
        type_account: select = self.session.execute(select(TypeTask))

        if type_task.raw.rowcount == 0:
            self.session.add(TypeTask(name="Выгрузить подписчиков"))
            self.session.add(TypeTask(name="Проверка на бота"))
            self.session.add(TypeTask(name="Выгрузка информации аккаунта"))
        if status.raw.rowcount == 0:
            self.session.add(Status(name="Выполнено"))
            self.session.add(Status(name="Ошибка"))

        if type_account.raw.rowcount == 0:
            self.session.add(TypeAccount(name="Человек"))
            self.session.add(TypeAccount(name="Бот"))

        self.session.commit()






# class db(object):
#     def __init__(self):
#         create_database()
#         self.cn: connection = psycopg2.connect(user=PS_USER,
#                                                password=PS_PASS,
#                                                host=PS_HOST,
#                                                port=PS_PORT,
#                                                database=PS_DATABASE)
#         self.cursor: cursor = self.cn.cursor()
#
#     def execute(self, sql):
#         self.cursor.execute(sql)
#         self.cn.commit()
#
#     def select(self, sql):
#         self.cursor.execute(sql)
#         record = self.cursor.fetchall()
#         return record
#
#     def insert(self, insert_query, items):
#         self.cursor.execute(insert_query, items)
#         self.cn.commit()
