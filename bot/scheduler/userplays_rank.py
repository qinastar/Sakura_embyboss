import math
import cn2an
from datetime import datetime, timezone, timedelta

from bot import bot, bot_photo, group, sakura_b, LOGGER, ranks, _open 
from bot.func_helper.emby import emby
from bot.func_helper.utils import convert_to_beijing_time, convert_s, cache, get_users, tem_deluser
from bot.sql_helper import Session
from bot.sql_helper.sql_emby import sql_get_emby, sql_update_embys, Emby, sql_update_emby
from bot.func_helper.fix_bottons import plays_list_button


class Uplaysinfo:
    client = emby

    @classmethod
    @cache.memoize(ttl=120)
    async def users_playback_list(cls, days):
        try:
            play_list = await emby.emby_cust_commit(user_id=None, days=days, method='sp')
        except Exception as e:
            print(f"Error fetching playback list: {e}")
            return None, 1, 1

        if play_list is None:
            return None, 1, 1

        with Session() as session:
            # 更高效地查询 Emby 表的数据
            result = session.query(Emby).filter(Emby.name.isnot(None)).all()

            if not result:
                return None, 1

            total_pages = math.ceil(len(play_list) / 10)
            members = await get_users()
            members_dict = {}

            for record in result:
                members_dict[record.name] = {
                    "name": members.get(record.tg, '未绑定bot或已删除'),
                    "tg": record.tg,
                    "lv": record.lv,
                    "iv": record.iv
                }

            rank_medals = ["🥇", "🥈", "🥉", "🏅"]
            rank_points = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]

            pages_data = []
            leaderboard_data = []

            for page_number in range(1, total_pages + 1):
                start_index = (page_number - 1) * 10
                end_index = start_index + 10
                page_data = f'**▎🏆{ranks.logo} {days} 天观影榜**\n\n'

                for rank, play_record in enumerate(play_list[start_index:end_index], start=start_index + 1):
                    medal = rank_medals[rank - 1] if rank < 4 else rank_medals[3]
                    member_info = members_dict.get(play_record[0], None)

                    if not member_info or not member_info["tg"]:
                        emby_name = '未绑定bot或已删除'
                        tg = 'None'
                    else:
                        emby_name = member_info["name"]
                        tg = member_info["tg"]

                        # 计算积分
                        points = rank_points[rank - 1] + (int(play_record[1]) // 60) if rank <= 10 else (
                                    int(play_record[1]) // 60)
                        new_iv = member_info["iv"] + points
                        leaderboard_data.append([member_info["tg"], new_iv, f'{medal}{emby_name}', points])

                    formatted_time = await convert_s(int(play_record[1]))
                    page_data += f'{medal}**第{cn2an.an2cn(rank)}名** | {emby_name}\n' \
                                 f'  观影时长 | {formatted_time}\n'

                page_data += f'\n#UPlaysRank {datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")}'
                pages_data.append(page_data)

            return pages_data, total_pages, leaderboard_data

    @staticmethod
    async def user_plays_rank(days=7, uplays=True):
        a, n, ls = await Uplaysinfo.users_playback_list(days)
        if not a:
            return await bot.send_photo(chat_id=group[0], photo=bot_photo,
                                        caption=f'🍥 星灵在汇聚星辰之力，过去{days}天星图活跃榜暂时无法绘制~ 请稍后再试吧！')
        play_button = await plays_list_button(n, 1, days)
        send = await bot.send_photo(chat_id=group[0], photo=bot_photo, caption=a[0], reply_markup=play_button)
        if uplays and _open.uplays:
            if sql_update_embys(some_list=ls, method='iv'):
                text = f'**✨ 星光奖励已发放！**\n\n'
                for i in ls:
                    text += f'一位幸运的冒险者获得了 {i[3]} {sakura_b}星尘奖励\n'
                n = 4096
                chunks = [text[i:i + n] for i in range(0, len(text), n)]
                for c in chunks:
                    await bot.send_message(chat_id=group[0],
                                           text=c + f'\n⏱️ 当前星辰时刻 - {datetime.now().strftime("%Y-%m-%d")}')
                LOGGER.info(f'【userplayrank】： ->成功 数据库执行批量操作{ls}')
            else:
                await send.reply(f'**🎂！！！星灵在分发星尘奖励时遇到宇宙风暴，请星域守护者关注~ **')
                LOGGER.error(f'【userplayrank】：-？失败 数据库执行批量操作{ls}')

    @staticmethod
    async def check_low_activity():
        now = datetime.now(timezone(timedelta(hours=8)))
        success, users = await emby.users()
        if not success:
            return await bot.send_message(chat_id=group[0], text='⭕ 调用emby api失败')
        msg = ''
        # print(users)
        for user in users:
            # 数据库先找
            e = sql_get_emby(tg=user["Name"])
            if e is None:
                continue

            elif e.lv == 'c':
                # print(e.tg)
                try:
                    ac_date = convert_to_beijing_time(user["LastActivityDate"])
                except KeyError:
                    ac_date = "None"
                finally:
                    if ac_date == "None" or ac_date + timedelta(days=15) < now:
                        if await emby.emby_del(id=e.embyid):
                            sql_update_emby(Emby.embyid == e.embyid, embyid=None, name=None, pwd=None, pwd2=None, lv='d',
                                            cr=None, ex=None)
                            tem_deluser()
                            msg += f'**🔋星光黯淡处理** - 一位迷失在星海的旅者因星图契约沉睡已久，被宇宙悄然回收。**\n\n'
                            LOGGER.info(f"【活跃检测】- 删除账户 {user['Name']} #id{e.tg}")
                        else:
                            msg += f'**🔋星光黯淡处理** - 一位迷失在星海的旅者因星图契约沉睡已久，宇宙回收未成功。**\n\n'
                            LOGGER.info(f"【活跃检测】- 删除账户失败 {user['Name']} #id{e.tg}")
            elif e.lv == 'b':
                try:
                    ac_date = convert_to_beijing_time(user["LastActivityDate"])
                    from bot import config
                    activity_check_days = config.activity_check_days
                    # print(e.name, ac_date, now)
                    if ac_date + timedelta(days=activity_check_days) < now:
                        if await emby.emby_change_policy(id=user["Id"], method=True):
                            sql_update_emby(Emby.embyid == user["Id"], lv='c')
                            msg += f"**🔋星光黯淡处理** - 一位沉睡的星际旅者，星光连续{activity_check_days}天未闪耀，星图契约将暂时沉睡。**\n\n"
                            LOGGER.info(f"【活跃检测】- 禁用账户 {user['Name']} #id{e.tg}：{activity_check_days}天未活跃")
                        else:
                            msg += f"**🎂星光黯淡处理** - 一位沉睡的星际旅者{activity_check_days}天未活跃，星图契约沉睡未能成功，请检查星之服务器连通性。**\n\n"
                            LOGGER.info(f"【活跃检测】- 禁用账户 {user['Name']} #id{e.tg}：禁用失败啦！检查emby连通性")
                except KeyError:
                    if await emby.emby_change_policy(id=user["Id"], method=True):
                        sql_update_emby(Emby.embyid == user["Id"], lv='c')
                        msg += f"**🔋星光黯淡处理** - 一位沉睡的星际旅者，注册后未闪耀星光，星图契约已暂时沉睡。**\n\n"
                        LOGGER.info(f"【活跃检测】- 禁用账户 {user['Name']} #id{e.tg}：注册后未活跃禁用")
                    else:
                        msg += f"**🎂星光黯淡处理** - 一位沉睡的星际旅者，注册后未闪耀星光，星图契约沉睡未能成功，请检查星之服务器连通性。**\n\n"
                        LOGGER.info(f"【活跃检测】- 禁用账户 {user['Name']} #id{e.tg}：禁用失败啦！检查emby连通性")
        n = 1000
        chunks = [msg[i:i + n] for i in range(0, len(msg), n)]
        for c in chunks:
            await bot.send_message(chat_id=group[0], text=c + f'**{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}**')