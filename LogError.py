import enum
from datetime import datetime as dt


class LogError(enum.Enum):
    out_of_proxies = 1


def print_log(text: str):
    print(f"{dt.now().strftime('%H:%M:%S')}: {text}")
