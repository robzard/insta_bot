from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, DateTime
from db_structure.tables import *

if __name__ == '__main__':
    # Создайте соединение с базой данных («тип базы данных + имя драйвера базы данных: // имя пользователя: пароль @ip адрес: порт / имя базы данных»)
    conn = "postgresql+psycopg2://selectel:selectel@5.53.125.70:5432/instagram"
    engine = create_engine(conn, encoding='UTF-8',
                           echo=False)  # echo = True означает выходной журнал выполнения, по умолчанию False

    # Удалить таблицу данных отображения (если она существует)
    b = Base.metadata.drop_all(engine)
    # Создать таблицу данных отображения (если она не существует)
    a=Base.metadata.create_all(engine)

    # Создать сессионный объект
    Session = sessionmaker(bind=engine)
    session = Session()

    """ CREATE """

    # Создать пользовательский объект
    status = Status(name="Зарегистрирован")
    type_task = TypeTask(name="Выгрузка подписчиков")
    session.add(status)
    session.add(type_task)
    session.commit()

    task = Task(status_id=1,
                type_id=1,
                date_start=datetime.now(),
                username="robzardmusic",
                id_username=123456789,
                username_worker="bot_45")



    # Добавить в сессию
    session.add(task)
    # Отправить в базу данных:
    session.commit()

    print(task.children.name)
    print('q')
