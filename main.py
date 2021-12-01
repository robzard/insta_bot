from DataBase import db
from Distributor import *


def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    db_ps = db()

    ds = Distributor(db_ps)
    ds.registration_tasks()
    ds.docker_run_containers()

    db_ps.cn.close()
    db_ps.cursor.close()

