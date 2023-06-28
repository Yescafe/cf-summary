import requests
import json
import datetime

API_PREFIX = 'https://codeforces.com/api/'
CONTEST_URL_FMT = 'https://codeforces.com/contests/{}'

class Contest:
    def __init__(self, name: str, cid: int, start_time: int, countdown: int, duration: int):
        self.name = name
        self.cid = cid
        self.url = CONTEST_URL_FMT.format(cid)
        # start time in UNIX timestamp
        self.start_time = start_time
        self.countdown = countdown
        # duration in seconds
        self.duration = duration
    def __repr__(self):
        return f'Contest(name: "{self.name}", cid: {self.cid}, url: "{self.url}", start_time: {self.start_time}, countdown: {self.countdown}, duration: {self.duration})'
    def __str__(self):
        return f'''## {self.name}
Contest ID: {self.cid}
Start time: {self.stringify_start_time()}
Countdown: {self.stringify_countdown()}
Duration: {self.stringify_duration()}
URL: {self.url}'''

    def stringify_interval(s: int):
        seconds, minutes, hours, days = s % 60, s // 60 % 60, s // 60 // 60 % 24, s // 60 // 60 // 24
        ret = ''
        if days > 0:
            ret += f'{days}d'
        if hours > 0:
            ret += f'{hours}h'
        if minutes > 0:
            ret += f'{minutes}m'
        if seconds > 0:
            ret += f'{seconds}s'
        return ret

    def stringify_duration(self):
        return Contest.stringify_interval(self.duration)
    def stringify_start_time(self):
        return str(datetime.datetime.fromtimestamp(self.start_time))
    def stringify_countdown(self):
        return Contest.stringify_interval(self.countdown)

def get_contests(time_limit = 48):
    api_url = API_PREFIX + 'contest.list'
    raw = requests.get(api_url)
    if raw.status_code != 200:
        return None
    # now data is a list of all cf contest info
    contests = json.loads(raw.text)['result']
    # translate time_limit in hours to seconds
    time_limit = time_limit * 3600
    ret = []
    for contest in contests:
        # relativeTimeSeconds = current - contest start time
        relative_time = int(contest['relativeTimeSeconds'])
        # past contests
        if relative_time > 0:
            break
        # future contests but not in time limit
        elif -relative_time > time_limit:
            continue
        # passed condition, create this CFContest and append it to ret
        name = contest['name']
        cid = int(contest['id'])
        start_time = int(contest['startTimeSeconds'])
        duration = int(contest['durationSeconds'])
        countdown = -relative_time
        ret.append(Contest(name=name, cid=cid, start_time=start_time, countdown=countdown, duration=duration))
    return ret

def get_contest_recent_one(time_limit = 7 * 24):
    cs = get_contests(time_limit)
    if len(cs) == 0:
        return None
    return cs[-1]

class User:
    def __init__(self, name: str, rating: int, rank: str):
        self.name = name
        self.rating = rating
        self.rank = rank
    def __repr__(self):
        return f'User(name: "{self.name}", rating: {self.rating}, rank: "{self.rank}")'
    def __str__(self):
        return f'- {self.name} - {self.rating} - {self.rank}'

def get_ratings(rating_sorted=True):
    # get handles from tokens.json
    with open('tokens.json', 'r+') as fp:
        raw = fp.read()
    tokens = json.loads(raw)
    handles = tokens['handles']
    # generate query URL
    api_url = API_PREFIX + 'user.info?handles={}'.format(';'.join(handles))
    raw_data = requests.get(api_url)
    if raw_data.status_code != 200:
        return None
    result = json.loads(raw_data.text)['result']
    ret = []
    for user in result:
        try:
            name = user['handle']
            rating = int(user['rating'])
            rank = user['rank']
            ret.append(User(name=name, rating=rating, rank=rank))
        except KeyError:
            continue

    if rating_sorted:
        ret.sort(key=lambda x: (-x.rating, x.name.lower()))
    else:
        ret.sort(key=lambda x: x.name.lower())

    return ret

class RatingChange:
    def __init__(self, cid: int, cname: str, name: str, rank: int, old_rat: int, new_rat: int):
        self.cid = cid
        self.cname = cname
        self.name = name
        self.rank = rank
        self.old_rat = old_rat
        self.new_rat = new_rat
    def __repr__(self):
        return f'RatingChange(cid: {self.cid}, cname: "{self.cname}", name: "{self.name}", rank: {self.rank}, old_rat: {self.old_rat}, new_rat: {self.new_rat})'
    def __str__(self):
        def explcit_sign(x: int):
            if x < 0:
                return str(x)
            else:
                return '+' + str(x)
        return f'- {self.name}({self.rank}): {self.old_rat} -> {self.new_rat} ({explcit_sign(self.new_rat - self.old_rat)})'

def get_rating_change(diff_sorted=True):
    # get handles from tokens.json
    with open('tokens.json', 'r+') as fp:
        raw = fp.read()
    tokens = json.loads(raw)
    handles = tokens['handles']

    QUERY_URL_FMT = API_PREFIX + 'user.rating?handle={}'
    latest_records = []
    for handle in handles:
        api_url = QUERY_URL_FMT.format(handle)
        raw_data = requests.get(api_url)
        if raw_data.status_code != 200:
            continue
        try:
            result = json.loads(raw_data.text)['result']
            if len(result) == 0:
                continue
            latest_contest = result[-1]

            cid = int(latest_contest['contestId'])
            cname = latest_contest['contestName']
            rank = int(latest_contest['rank'])
            old_rat = int(latest_contest['oldRating'])
            new_rat = int(latest_contest['newRating'])

            latest_records.append(RatingChange(cid=cid, cname=cname, name=handle, rank=rank, old_rat=old_rat, new_rat=new_rat))
        except ValueError:
            continue

    if len(latest_records) == 0:
        return latest_records

    latest_records.sort(key=lambda x: (-x.cid))
    recent_contest_id = latest_records[0].cid
    ret = []
    for record in latest_records:
        if record.cid != recent_contest_id:
            break
        ret.append(record)

    if diff_sorted:
        ret.sort(key=lambda x: x.old_rat - x.new_rat)
    else:
        ret.sort(key=lambda x: x.rank)

    return ret

if __name__ == '__main__':
    print(get_contests())

