from pycqBot.cqApi import cqHttpApi, cqLog
import logging
import utils.tokens
import apis.qqbot.cf as qqbot_cf_apis
import utils.db
from utils.time import get_readable_time
from apis.qqbot.cf import FakeMessage

def main():
    cqLog(logging.DEBUG)
    cqapi = cqHttpApi()
    tokens = utils.tokens.get_tokens()

    bot = cqapi.create_bot(
        group_id_list=tokens['groups'],
        options={ 'admin': tokens['admins'] },
    )

    def bot_bind_command(f, fname: str, help: str = None):
        nonlocal bot
        if help is not None:
            bot.command(f, fname, { 'help': [f'#{fname} - {help}'] })
        else:
            bot.command(f, fname)

    bot_bind_command(qqbot_cf_apis.ping, 'ping', '测试')
    bot_bind_command(qqbot_cf_apis.cf, 'cc', '获取 48 小时内的 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cf1, 'cc1', '获取 7 天内最近的一场 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cfr, 'r', '获取名单上成员的 Codeforces 竞赛分')
    bot_bind_command(qqbot_cf_apis.cfc, 'rc', '获取名单上成员的最近一场的 Codeforces 竞赛分变动')
    bot_bind_command(qqbot_cf_apis.cp, 'cp', '获取某一个竞赛的题单和信息 (WIP)')
    bot_bind_command(qqbot_cf_apis.regular_update, 'db-update', '与 Codeforces 服务器同步数据库')
    bot_bind_command(qqbot_cf_apis.force_update, 'db-force-update', '重建数据库')
    bot_bind_command(qqbot_cf_apis.db_health, 'db-health', '数据库健康信息')

    # 中文关键词
    bot_bind_command(qqbot_cf_apis.cf, '竞赛', '获取 48 小时内的 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cf1, '一场竞赛', '获取 7 天内最近的一场 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cfr, '竞赛分', '获取名单上成员的 Codeforces 竞赛分')
    bot_bind_command(qqbot_cf_apis.cfc, '变动', '获取名单上成员的最近一场的 Codeforces 竞赛分变动')

    utils.db.init_db()

    def bot_bind_reminder(f, fname: str, time_sleep_hours: int, help_name: str = None):
        time_sleep = time_sleep_hours * 3600
        bot.timing(f, fname, { 'timeSleep': time_sleep })

    def timing_db_update(from_id):
        ts, errno, _ = utils.db.update_db()
        if errno == 0:
            return
        cqapi.send_group_msg(from_id, f'于 {get_readable_time(ts)} 定时更新出错，请检查后台。')
    bot_bind_reminder(timing_db_update, 'timing_db_update', 8, '定时同步数据库')

    def timing_cf_reminder(from_id):
        HOURS = 48
        contests = utils.db.get_recent_contests(time_limit=HOURS)
        if len(contests) > 0:
            message = FakeMessage()
            message.reply(f'最近 {HOURS} 小时内的 Codeforces 竞赛提醒：\n' + '\n'.join(str(c) for c in contests))
            cqapi.send_group_msg(from_id, message.get())
    bot_bind_reminder(timing_cf_reminder, 'timing_cf_reminder', 8, '定时提醒最近 48 小时内的 Codeforces 竞赛')

    bot.start()

if __name__ == '__main__':
    main()
