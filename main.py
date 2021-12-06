from db_structure.DataBase import db
from Distributor import *

if __name__ == '__main__':
    db_ps = db()

    ds = Distributor(db_ps)
    ds.registration_tasks()
    #ds.docker_run_containers()

    # db_ps.cn.close()
    # db_ps.cursor.close()

