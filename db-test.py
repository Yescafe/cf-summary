import utils.db as db
from utils.time import get_readable_time

if __name__ == '__main__':
    print(db.init_db())
    print(db.update_db())
    print(db.update_db())

    print(db.get_recent_contests(time_limit=30 * 24))

    print(db.get_ratings())
    print(db.get_rating_change())
    print(get_readable_time(db.get_latest_succeed_time()))

    db.CURSOR.execute('select * from logs')
    print(db.CURSOR.fetchall())

    print(db.get_latest_log())
