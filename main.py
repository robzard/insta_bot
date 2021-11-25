from DataBase import db
from Distributor import *


def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    db = db()
    a = db.select("SELECT * FROM test limit 1")

    ds = Distributor(db)
    ds.registration_tasks
    ds.docker_run_containers

    db.cn.close()
    db.cursor.close()

