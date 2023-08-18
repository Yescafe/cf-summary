from pycqBot.cqApi import cqHttpApi, cqLog
from pycqBot import Message
import logging
import utils.tokens
import apis.qqbot.cf as qqbot_cf_apis

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

    bot.start()

if __name__ == '__main__':
    main()
