from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, DateTime, Date, JSON
from sqlalchemy.orm import relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = 'queue_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('types_task.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False)
    date_start = Column(DateTime, nullable=True)
    date_end = Column(DateTime, nullable=True)
    id_docker_container = Column(Integer, nullable=True)
    username = Column(String(64), nullable=False)
    id_username = Column(Integer, nullable=True)
    username_worker = Column(String(64), nullable=True)
    result_data_json = Column(JSON, nullable=True)
    log_error = Column(String(1024), nullable=True)

    children = relationship("TypeTask", back_populates="parent")


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('types_account.id'), nullable=False)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    proxy = Column(String(256), nullable=False)
    user_agent = Column(String(4028), nullable=False)
    active = Column(Integer, nullable=False)
    comment = Column(String(4028), nullable=False)


class TypeTask(Base):
    __tablename__ = 'types_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    parent = relationship("Task", back_populates="children")


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)


class TypeAccount(Base):
    __tablename__ = 'types_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)


