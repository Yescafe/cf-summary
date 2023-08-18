from pycqBot import Message
import services.cf

def _err(message: Message):
    message.reply('获取 Codeforces 竞赛列表失败，请查看后台。')
    # TODO handle errors

def ping(_, message: Message):
    message.reply('pong')

def cf(_, message: Message):
    contests = services.cf.get_contests()
    if contests is None:
        _err(message)
    elif len(contests) == 0:
        message.reply('最近 48 小时无 Codeforces 竞赛。')
    else:
        message.reply('\n'.join(str(c) for c in contests))

def cf1(_, message: Message):
    contest = services.cf.get_contest_recent_one()
    if contest is None:
        message.reply('没有获取到最近 7 天内的 Codeforces 竞赛。')
    else:
        message.reply(str(contest))

def cfr(_, message: Message):
    lst_users = services.cf.get_ratings()
    if lst_users is None:
        _err(message)
    else:
        message.reply('\n'.join(str(u) for u in lst_users))

def cfc(_, message: Message):
    lst_rating_change = services.cf.get_rating_change()
    if lst_rating_change is None:
        _err(message)
    elif len(lst_rating_change) == 0:
        message.reply('无信息。')
    else:
        message.reply(f'## {lst_rating_change[0].cname}\n' + '\n'.join(str(rc) for rc in lst_rating_change))
