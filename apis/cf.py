import services.cf

def instruction_cf(params):
    maybe_time_limit = None
    try:
        maybe_time_limit = int(params)
    except ValueError:
        pass

    if maybe_time_limit is None:
        res = services.cf.get_contests()
    else:
        res = services.cf.get_contests(time_limit=maybe_time_limit)

    if res is None:
        return None
    if len(res) == 0:
        return 'No coming soon contest.'

    return '\n'.join(str(c) for c in res)

def instruction_cf1(params):
    maybe_time_limit = None
    try:
        maybe_time_limit = int(params)
    except ValueError:
        pass

    if maybe_time_limit is None:
        res = services.cf.get_contest_recent_one()
    else:
        res = services.cf.get_contest_recent_one(time_limit=maybe_time_limit)

    if res is None:
        return None
    if len(res) == 0:
        return 'No coming soon contest.'

    return str(res)

def instruction_cfr(params):
    maybe_rating_sorted = None
    if params == '--by-name' or params == '-n':
        maybe_rating_sorted = False
    elif params == '--by-rating' or params == '-r':
        maybe_rating_sorted = True

    if maybe_rating_sorted is None:
        res = services.cf.get_ratings()
    else:
        res = services.cf.get_ratings(rating_sorted=maybe_rating_sorted)

    if res is None:
        return None
    if len(res) == 0:
        return 'No data.'

    return '\n'.join(str(u) for u in res)

def instruction_cfc(params):
    maybe_diff_sorted = None
    if params == '--by-rank' or params == '-r':
        maybe_diff_sorted = False
    elif params == '--by-diff' or params == '-d':
        maybe_diff_sorted = True

    if maybe_diff_sorted is None:
        res = services.cf.get_rating_change()
    else:
        res = services.cf.get_rating_change(diff_sorted=maybe_diff_sorted)

    if res is None:
        return None
    if len(res) == 0:
        return 'No data.'

    return f'## {res[0].cname}\n' + '\n'.join(str(rc) for rc in res)
