import utils.db as db
from utils.time import get_readable_time

if __name__ == '__main__':
    db.init_db()
    db.update_db()

    print(db.get_recent_contests(time_limit=30 * 24))
    print(f'db updated at {db.get_latest_log()[0]}')

    print(db.get_ratings())
    print(db.get_rating_change())
    print(get_readable_time(db.get_latest_succeed_time()))
