import enum


class TypeTask(enum.Enum):
    load_followers = 1
    check_bot = 2
    load_information = 3


class RequestInstagram(enum.Enum):
    get_id_from_username = 1
    load_followers = 2