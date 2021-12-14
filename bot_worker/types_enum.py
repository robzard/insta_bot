import enum


class TypesTask(enum.Enum):
    load_followers = 1
    load_information = 2
    check_bot = 3


class RequestInstagram(enum.Enum):
    get_id_from_username = 1
    load_followers = 2
    load_info_follower = 3
    get_media_id = 4


class StatusTask(enum.Enum):
    registered = 1
    in_work = 2
    success = 3
    error = 4
