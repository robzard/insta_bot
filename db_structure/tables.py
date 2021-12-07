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
    date_add = Column(DateTime, nullable=False)
    date_start = Column(DateTime, nullable=True)
    date_end = Column(DateTime, nullable=True)
    id_docker_container = Column(Integer, nullable=True)
    username = Column(String(64), nullable=False)
    id_username = Column(Integer, nullable=True)
    username_worker = Column(String(64), nullable=True)
    id_username_parent = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    result_data_json = Column(JSON, nullable=True)
    log_error = Column(String(), nullable=True)

    # children = relationship("AccountSettings", back_populates="parent")


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('types_account.id'), nullable=False)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    proxy_id = Column(Integer, ForeignKey('proxy.id'), nullable=True)
    user_agent_id = Column(Integer, ForeignKey('user_agents.id'), nullable=True)
    work_now = Column(Integer, nullable=True)
    active = Column(Integer, nullable=False)
    comment = Column(String(), nullable=True)
    account_settings = relationship("AccountSettings", uselist=False, backref="accounts")
    log_error = Column(String(), nullable=True)
    count_requests = Column(Integer, nullable=True)
    date_last_request = Column(DateTime, nullable=True)

    tasks = relationship("Task", uselist=True, backref="accounts", lazy="dynamic")
    proxy = relationship("Proxy", backref="accounts")
    user_agent = relationship("UserAgent", backref="accounts")


class TypeTask(Base):
    __tablename__ = 'types_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)

    def __init__(self, name: str):
        self.name = name


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)

    def __init__(self, name: str):
        self.name = name


class TypeAccount(Base):
    __tablename__ = 'types_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)

    def __init__(self, name: str):
        self.name = name


class AccountSettings(Base):
    __tablename__ = 'account_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_account = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    source_accounts = Column(String(1024), nullable=False)

    def __init__(self, id_account: int, source_accounts: str):
        self.id_account = id_account
        self.source_accounts = source_accounts


class Proxy(Base):
    __tablename__ = 'proxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    proxy_value = Column(String(512), nullable=False)

    def __init__(self, proxy_value: str):
        self.proxy_value = proxy_value


class UserAgent(Base):
    __tablename__ = 'user_agents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_agent_value = Column(String(), nullable=False)

    def __init__(self, user_agent_value: str):
        self.proxy_value = user_agent_value
