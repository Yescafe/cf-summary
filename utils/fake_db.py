import services.cf as cfs
import json
import time

def toJson(a):
    return json.dumps(a, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def init_db(force=False):
    update_db()

ITEMS = {
    'contests': lambda: cfs.get_contests(time_limit=30 * 24),
    'ratings': cfs.get_ratings,
    'rating_change': cfs.get_rating_change,
}

def update_db() -> str:
    for name, func in ITEMS.items():
        print(f'=== Updating {name}')
        lst = func()
        if lst is None:
            return f"can't fetch {name}"
        with open(f'data_{name}.json', 'w') as fp:
            try:
                fp.write(toJson(lst))
            except:
                return f"can't store to data_{name}.json"

def get_recent_contests(time_limit: int = 48):
    time_limit *= 3600
    try:
        with open('data_contests.json', 'r') as fp:
            j = json.load(fp)
    except:
        return []
    contests = [cfs.Contest(**c) for c in j]

    ret = []
    current_time = int(time.time())
    for contest in contests:
        relative_time = current_time - contest.start_time
        if relative_time > 0:
            break
        elif -relative_time > time_limit:
            continue
        ret.append(contest)

    return ret[::-1]

def get_one_recent_contest(time_limit: int = 7 * 24):
    contests = get_recent_contests(time_limit=time_limit)
    if len(contests) == 0:
        return None
    return contests[0]

def get_ratings():
    try:
        with open('data_ratings.json') as fp:
            j = json.load(fp)
    except:
        return []

    return [cfs.User(**u) for u in j]

def get_rating_change():
    try:
        with open('data_rating_change.json') as fp:
            j = json.load(fp)
    except:
        return []

    return [cfs.RatingChange(**c) for c in j]
