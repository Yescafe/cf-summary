from pycqBot import Message
import utils.db as db
from utils.time import get_readable_time
import services.cf as cfs

def _err(message: Message):
    # TODO never reach?
    message.reply('未知错误，请查看后台。')
    # TODO handle errors

def ping(_, message: Message):
    message.reply('pong')

class FakeMessage:
    def __init__(self):
        self.msg = ''
    def reply(self, msg: str):
        self.msg += msg
    def get(self):
        return self.msg.strip() + f'\n\n（该数据于 {get_readable_time(db.get_latest_succeed_time())} 更新，仅供参考）'

def cf(_, message_: Message):
    message = FakeMessage()
    contests = db.get_recent_contests()
    if contests is None:
        _err(message)
    elif len(contests) == 0:
        message.reply('最近 48 小时内无 Codeforces 竞赛。')
    else:
        message.reply('\n\n'.join(str(c) for c in contests))
    message_.reply(message.get())

def cf1(_, message_: Message):
    message = FakeMessage()
    contest = db.get_one_recent_contest()
    if contest is None:
        message.reply('最近 7 天内无 Codeforces 竞赛。')
    else:
        message.reply(str(contest))
    message_.reply(message.get())

def cfr(_, message_: Message):
    message = FakeMessage()
    lst_users = db.get_ratings()
    if lst_users is None:
        _err(message)
    else:
        message.reply('\n'.join(str(u) for u in lst_users))
    message_.reply(message.get())

def cfc(_, message_: Message):
    message = FakeMessage()
    lst_rating_change = db.get_rating_change()
    if lst_rating_change is None:
        _err(message)
    elif len(lst_rating_change) == 0:
        message.reply('无信息。')
    else:
        message.reply(f'## {lst_rating_change[0].cname}\n' + '\n'.join(str(rc) for rc in lst_rating_change))
    message_.reply(message.get())

def regular_update(_, message: Message):
    message.reply('正在更新数据库数据…')
    ts, errno, log = db.update_db()
    if errno != 0:
        message.reply(f'更新出错，出错代码 {errno}，详细信息：{log[:100]}...。可尝试重建数据库。')
    else:
        message.reply(f'于 {get_readable_time(ts)} 更新成功。')

def force_update(_, message: Message):
    message.reply('正在重建数据库数据…')
    ts, errno, log = db.force_update_db()
    if errno != 0:
        message.reply(f'更新出错，出错代码 {errno}，详细信息：{log[:100]}...。')
    else:
        message.reply(f'于 {get_readable_time(ts)} 更新成功。')

def db_health(_, message: Message):
    latest_log = db.get_latest_log()
    succ_time, try_time = db.get_latest_succeed_time(), latest_log[0]

    msg = ''
    msg += f'上次尝试更新时间：{get_readable_time(try_time)}\n'
    msg += f'上次成功更新时间：{get_readable_time(succ_time)}\n'

    if succ_time != try_time:
        msg += f'失败原因：Errno {latest_log[1]}，{latest_log[2][:200]}\n'

    message.reply(msg.strip())

def cp(params, message: Message):
    cid = int(' '.join(params))
    contest, problems = cfs.get_contest_problems(cid)

    if contest is None or problems is None:
        message.reply('获取竞赛题失败，请检查竞赛 ID 是否合法。')
        return

    msg = ''
    msg += f'## {contest.name}\n'
    msg += f'URL: {contest.url}\n'
    for p in problems:
        msg += str(p) + '\n'

    message.reply(msg.strip())
