import psycopg2
from psycopg2 import Error
from psycopg2._psycopg import connection, cursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import *


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
        self.cn: connection = psycopg2.connect(user=PS_USER,
                                               password=PS_PASS,
                                               host=PS_HOST,
                                               port=PS_PORT,
                                               database=PS_DATABASE)
        self.cursor: cursor = self.cn.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)
        self.cn.commit()

    def select(self, sql):
        self.cursor.execute(sql)
        record = self.cursor.fetchall()
        return record

    def insert(self, insert_query, items):
        self.cursor.execute(insert_query, items)
        self.cn.commit()
