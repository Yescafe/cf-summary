from pycqBot.cqApi import cqHttpApi, cqLog
import logging
import utils.tokens
import apis.qqbot.cf as qqbot_cf_apis
import utils.db
from utils.time import get_readable_time

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
    bot_bind_command(qqbot_cf_apis.cf, 'cf', '获取 48 小时内的 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cf1, 'cf1', '获取 7 天内最近的一场 Codeforces 竞赛')
    bot_bind_command(qqbot_cf_apis.cfr, 'cfr', '获取名单上成员的 Codeforces 竞赛分')
    bot_bind_command(qqbot_cf_apis.cfc, 'cfc', '获取名单上成员的最近一场的 Codeforces 竞赛分变动')
    bot_bind_command(qqbot_cf_apis.regular_update, 'db-update', '与 Codeforces 服务器同步数据库')
    bot_bind_command(qqbot_cf_apis.force_update, 'db-force-update', '重建数据库')
    bot_bind_command(qqbot_cf_apis.db_health, 'db-health', '数据库健康信息')

    utils.db.init_db()

    def timing_db_update(from_id):
        ts, errno, _ = utils.db.update_db()
        if errno == 0:
            return
        cqapi.send_group_msg(from_id, f'于 {get_readable_time(ts)} 定时更新出错，请检查后台。')
    bot.timing(timing_db_update, 'timing_db_update', { 'timeSleep': 28800 })

    bot.start()

if __name__ == '__main__':
    main()
