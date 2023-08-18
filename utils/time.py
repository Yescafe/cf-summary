import time
import datetime

def get_readable_time(timestamp: int) -> str:
    if timestamp < 0:
        return '几亿年前'
    t = datetime.datetime.fromtimestamp(timestamp)
    return str(t)
