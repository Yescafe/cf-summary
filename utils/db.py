import pymysql
from utils.tokens import get_tokens
import services.cf as cfs
import time

CONN = None
CURSOR = None

def prepare_rating_change():
    if CURSOR is None:
        return

    try:
        CURSOR.execute(r'drop table rating_change')
    except:
        print('drop rating_change failed')

    CURSOR.execute(r'''create table rating_change(
    cid int,
    cname varchar(200),
    name varchar(100),
    `rank` varchar(20),
    old_rat int,
    new_rat int,
    primary key (name)
)''')


def init_db(force=False):
    global CONN
    global CURSOR

    if not force and (CONN is not None or CURSOR is not None):
        return

    tokens = get_tokens()
    CONN = pymysql.connect(
        host=tokens['mysql_host'],
        port=tokens['mysql_port'],
        user=tokens['mysql_username'],
        password=tokens['mysql_password'],
        db=tokens['mysql_dbname']
    )

    CURSOR = CONN.cursor()
    # CURSOR.execute(f'use {tokens["mysql_dbname"]}')

    try:
        CURSOR.execute(r'drop table contests')
    except:
        print('drop contests failed')
    try:
        CURSOR.execute(r'drop table users')
    except:
        print('drop users failed')
    try:
        CURSOR.execute(r'drop table logs')
    except:
        print('drop logs failed')

    CURSOR.execute(r'''create table contests(
    cid int not null,
    name varchar(200),
    start_time bigint,
    duration int,
    primary key (cid)
)''')
    CURSOR.execute(r'''create table users(
    name varchar(100) not null,
    rating int,
    `rank` varchar(20),
    primary key (name)
)''')
    CURSOR.execute(r'''create table logs(
    `id` int NOT NULL AUTO_INCREMENT,
    errno int,
    verbose varchar(1024),
    timestamp int,
    primary key (`id`)
)''')

    print('=== Finish to initialize database')

E_DB, E_CONTESTS, E_RATINGS, E_RCHANGE = 1, 2, 4, 8

def update_db() -> (int, int, str):
    if CONN is None or CURSOR is None:
        return (E_DB, 'Database may be not initialized, try to use force update instead.')

    errno = 0
    log = ''
    def log_append(msg: str):
        nonlocal log
        log += msg + '; '

    print('=== Updating contests')
    contests = cfs.get_contests(time_limit=30 * 24)
    if contests is None:
        errno |= E_CONTESTS
        log_append('contests is None')
    else:
        for c in contests:
            QUERY = r'replace into contests (cid, name, start_time, duration) values (%s, %s, %s, %s)'
            PARAMS = (c.cid, c.name, c.start_time, c.duration)
            try:
                CURSOR.execute(QUERY, PARAMS)
            except:
                errno |= E_DB
                log_append(f'query `{QUERY}` failed, params: `{PARAMS}`')

    print('=== Updating users')
    users = cfs.get_ratings()
    if users is None:
        errno |= E_RATINGS
        log_append('users is None')
    else:
        for u in users:
            QUERY = r'replace into users (name, rating, `rank`) values (%s, %s, %s)'
            PARAMS = (u.name, u.rating, u.rank)
            try:
                CURSOR.execute(QUERY, PARAMS)
            except:
                errno |= E_DB
                log_append(f'query `{QUERY}` failed, params: `{PARAMS}`')

    print('=== Updating rating_change')
    prepare_rating_change()
    rating_change = cfs.get_rating_change()
    if rating_change is None:
        errno | E_RCHANGE
        log_append('rating_change is None')
    else:
        for rc in rating_change:
            QUERY = r'replace into rating_change (cid, cname, name, `rank`, old_rat, new_rat) values (%s, %s, %s, %s, %s, %s)'
            PARAMS = (rc.cid, rc.cname, rc.name, rc.rank, rc.old_rat, rc.new_rat)
            try:
                CURSOR.execute(QUERY, PARAMS)
            except:
                errno |= E_DB
                log_append(f'query `{QUERY}` failed, params: `{PARAMS}`')

    if errno == 0:
        log = 'Up-to-date.'

    print('=== Updating logs')
    current_timestamp = int(time.time())
    QUERY = r'insert into logs (errno, verbose, timestamp) values (%s, %s, %s)'
    PARAMS = (errno, log, current_timestamp)
    try:
        CURSOR.execute(QUERY, PARAMS)
    except:
        errno |= E_DB
        log_append(f'query `{QUERY}` failed, params: `{PARAMS}`')

    CONN.commit()

    return current_timestamp, errno, log

def force_update_db():
    init_db(force=True)
    return update_db()

def get_latest_log() -> (int, int, str):
    if CURSOR is None:
        return (-1, None)

    CURSOR.execute(r'select * from logs order by timestamp desc limit 1')
    _, errno, log, timestamp = CURSOR.fetchone()

    return timestamp, errno, log

def get_latest_succeed_time() -> int:
    if CURSOR is None:
        return -1

    CURSOR.execute(r'select * from logs order by timestamp desc')
    raw_logs = CURSOR.fetchall()

    for rl in raw_logs:
        if rl[1] == 0:
            return rl[3]
    return -1

def get_recent_contests(time_limit: int = 48):
    time_limit *= 3600    # hours to seconds

    try:
        CURSOR.execute(r'select * from contests order by start_time desc')
    except:
        return []
    raw_contests = CURSOR.fetchall()

    ret = []
    current_time = int(time.time())
    for rc in raw_contests:
        relative_time = current_time - rc[2]
        if relative_time > 0:
            break
        elif -relative_time > time_limit:
            continue

        name, cid, start_time, duration = rc
        countdown = -relative_time
        ret.append(cfs.Contest(name=name, cid=cid, start_time=start_time, countdown=countdown, duration=duration))

    return ret[::-1]

def get_one_recent_contest(time_limit: int = 7 * 24):
    contests = get_recent_contests(time_limit=time_limit)
    if len(contests) == 0:
        return None
    return contests[0]

def get_ratings():
    try:
        CURSOR.execute(r'select * from users order by rating desc')
    except:
        return []
    raw_users = CURSOR.fetchall()

    ret = []
    for ru in raw_users:
        name, rating, rank = ru
        ret.append(cfs.User(name=name, rating=rating, rank=rank))

    return ret

def get_rating_change():
    try:
        CURSOR.execute(r'select * from rating_change')
    except:
        return []
    raw_rating_change = CURSOR.fetchall()

    ret = []
    for rrc in raw_rating_change:
        cid, cname, name, rank, old_rat, new_rat = rrc
        ret.append(cfs.RatingChange(cid=cid, cname=cname, name=name, rank=rank, old_rat=old_rat, new_rat=new_rat))

    ret.sort(key=lambda x: x.old_rat - x.new_rat)

    return ret
