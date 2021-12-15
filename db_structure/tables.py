from datetime import datetime

from sqlalchemy.orm import sessionmaker, backref
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
    username_worker = Column(String(64), nullable=True)
    id_username_parent = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    log_error = Column(String(), nullable=True)

    follower_data = relationship("UserData", backref="followers_data")


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('types_account.id'), nullable=False)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    work_now = Column(Integer, nullable=True)
    active = Column(Integer, nullable=False)
    comment = Column(String(), nullable=True)
    log_error = Column(String(), nullable=True)
    user_agent_id = Column(Integer, ForeignKey('user_agents.id'), nullable=True)
    count_requests = Column(Integer, nullable=True)
    date_last_request = Column(DateTime, nullable=True)

    account_settings = relationship("AccountSettings", uselist=False, backref="accounts")
    tasks = relationship("Task", uselist=True, backref="accounts", lazy="dynamic")
    proxy = relationship("Proxy", uselist=False, backref="accounts")
    user_agent = relationship("UserAgent", uselist=False, backref="user_agents")


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
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    proxy_value = Column(String(1024), nullable=False)
    id_account = Column(Integer, ForeignKey('accounts.id'), nullable=True)

    def __init__(self, proxy_value: str):
        self.proxy_value = proxy_value


class UserAgent(Base):
    __tablename__ = 'user_agents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_agents_value = Column(String(), nullable=False)

    def __init__(self, user_agents_value: str):
        self.user_agents_value = user_agents_value


class UserData(Base):
    __tablename__ = 'followers_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String())
    user_id_profile = Column(String())
    post_id_profile = Column(String())
    pic_url_profile = Column(String())
    media_count_profile = Column(Integer())
    follower_count_profile = Column(Integer())
    following_count_profile = Column(Integer())
    username_donor = Column(String())
    task_id = Column(Integer, ForeignKey("queue_tasks.id"))
    is_bot = Column(Integer())

    def __init__(self, username: str = None,
                 user_id_profile: str = None,
                 post_id_profile: str = None,
                 pic_url_profile: str = None,
                 media_count_profile: int = None,
                 follower_count_profile: int = None,
                 following_count_profile: int = None,
                 username_donor: str = None):
        self.username = username
        self.user_id_profile = user_id_profile
        self.post_id_instagram = post_id_profile
        self.pic_url_profile = pic_url_profile
        self.media_count_profile = media_count_profile
        self.follower_count_profile = follower_count_profile
        self.following_count_profile = following_count_profile
        self.username_donor = username_donor


class Donor(Base):
    __tablename__ = 'instagram_donors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(), nullable=False)
    id_instagram = Column(String())

    def __init__(self, username: str, id_instagram: str):
        self.username = username
        self.id_instagram = id_instagram


class LogErrorWrite(Base):
    __tablename__ = 'log_error'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer(), ForeignKey("queue_tasks.id"))
    account_id = Column(Integer(), ForeignKey("accounts.id"))
    filename = Column(String())
    lineno = Column(Integer())
    function = Column(String())
    code_context = Column(String())
    description = Column(String())
    type_error = Column(String())
    date_error = Column(DateTime())

    def __init__(self,
                 task_id: int = None,
                 account_id: int = None,
                 filename: str = "",
                 lineno: int = None,
                 function: str = None,
                 code_context: str = None,
                 description: str = None,
                 type_error: str = None,
                 date_error: datetime = datetime.now()):
        self.task_id = task_id
        self.account_id = account_id
        self.filename = filename
        self.lineno = lineno
        self.function = function
        self.code_context = code_context
        self.description = description
        self.type_error = type_error
        self.date_error = date_error
