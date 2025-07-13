from cacheout import Cache
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram.types import InlineKeyboardMarkup
from pyromod.helpers import ikb, array_chunk
from bot import chanel, main_group, bot_name, extra_emby_libs, tz_id, tz_ad, tz_api, _open, sakura_b, \
    schedall, auto_update, fuxx_pitao, kk_gift_days, moviepilot, red_envelope
from bot.func_helper import nezha_res
from bot.func_helper.emby import emby
from bot.func_helper.utils import members_info

cache = Cache()

"""start面板 ↓"""


def judge_start_ikb(is_admin: bool, account: bool) -> InlineKeyboardMarkup:
    """
    start面板按钮
    """
    if not account:
        d = []
        d.append(['🎟️ 使用星符', 'exchange'])
        d.append(['👑 签订星图契约', 'create'])
        d.append(['⭕ 星图契约迁跃', 'changetg'])
        d.append(['🔍 绑定星图档案', 'bindtg'])
        # 如果邀请等级为d （未注册用户也能使用），则显示兑换商店
        if _open.invite_lv == 'd':
            d.append(['🏪 星尘兑换中心', 'storeall'])
    else:
        d = [['️👥 冒险者面板', 'members'], ['🌐 星之服务器', 'server']]
        if schedall.check_ex: d.append(['🎟️ 使用续期星符', 'exchange'])
    if _open.checkin: d.append([f'🎯 星辰签到', 'checkin'])
    lines = array_chunk(d, 2)
    if is_admin: lines.append([['👮🏻‍♂️ 星域守护者面板', 'manage']])
    keyword = ikb(lines)
    return keyword


# un_group_answer
group_f = ikb([[('✨ 与星灵沟通 ✨', f't.me/{bot_name}', 'url')]])
# un in group
judge_group_ikb = ikb([[('🌟 星光频道 ', f't.me/{chanel}', 'url'),
                        ('💫 冒险者公会', f't.me/{main_group}', 'url')],
                       [('❌ 湮灭此消息', 'closeit')]])

"""members ↓"""


def members_ikb(is_admin: bool = False, account: bool = False) -> InlineKeyboardMarkup:
    """
    判断用户面板
    """
    if account:
        normal = [[('🏪 兑换商店', 'storeall'), ('🗑️ 删除账号', 'delme')],
                    [('🎬 显示/隐藏', 'embyblock'), ('⭕ 重置密码', 'reset')],
                    [('💖 我的收藏', 'my_favorites'),('💠 我的设备', 'my_devices')],
                    ]
        if moviepilot.status:
            normal.append([['🍿 星域点播站', 'download_center']])
        normal.append([['♻️ 返回星港', 'back_start']])
        return ikb(normal)
    else:
        return judge_start_ikb(is_admin, account)
        # return ikb(
        #     [[('👑 创建账户', 'create')], [('⭕ 换绑TG', 'changetg'), ('🔍 绑定TG', 'bindtg')],
        #      [('♻️ 主界面', 'back_start')]])


back_start_ikb = ikb([[('💫 返回星港', 'back_start')]])
back_members_ikb = ikb([[('💨 返回', 'members')]])
back_manage_ikb = ikb([[('💨 返回', 'manage')]])
re_create_ikb = ikb([[('🍥 重新发送星语', 'create'), ('💫 返回星港', 'members')]])
re_changetg_ikb = ikb([[('✨ 星图契约迁跃', 'changetg'), ('💫 返回星港', 'members')]])
re_bindtg_ikb = ikb([[('✨ 绑定星图档案', 'bindtg'), ('💫 返回星港', 'members')]])
re_delme_ikb = ikb([[('♻️ 重新尝试', 'delme')], [('🔙 返回', 'members')]])
re_reset_ikb = ikb([[('♻️ 重新尝试', 'reset')], [('🔙 返回', 'members')]])
re_exchange_b_ikb = ikb([[('♻️ 重新尝试', 'exchange'), ('❌ 湮灭', 'closeit')]])
re_born_ikb = ikb([[('✨ 重新发送星语', 'store-reborn'), ('💫 返回', 'storeall')]])


def send_changetg_ikb(cr_id, rp_id):
    """
    :param cr_id: 当前操作id
    :param rp_id: 替换id
    :return:
    """
    return ikb([[('✅ 批准迁跃', f'changetg_{cr_id}_{rp_id}'), ('❎ 驳回请求', f'nochangetg_{cr_id}_{rp_id}')]])


def store_ikb():
    return ikb([[(f'♾️ 兑换星域白名单', 'store-whitelist'), (f'🔥 兑换星图唤醒', 'store-reborn')],
                [(f'🎟️ 兑换星符', 'store-invite'), (f'🔍 查询已生成星符', 'store-query')],
                [('❌ 湮灭', 'members')]])


re_store_renew = ikb([[('✨ 重新发送星语', 'changetg'), ('💫 取消星语', 'storeall')]])


def del_me_ikb(embyid) -> InlineKeyboardMarkup:
    return ikb([[('🎯 确认回收', f'delemby-{embyid}')], [('🔙 取消', 'members')]])


def emby_block_ikb(embyid) -> InlineKeyboardMarkup:
    return ikb(
        [[("✔️️ - 显示星路", f"emby_unblock-{embyid}"), ("✖️ - 隐藏星路", f"emby_block-{embyid}")], [("🔙 返回", "members")]])


user_emby_block_ikb = ikb([[('✅ 已隐藏星路', 'members')]])
user_emby_unblock_ikb = ikb([[('❎ 已显示星路', 'members')]])

"""server ↓"""


@cache.memoize(ttl=120)
async def cr_page_server():
    """
    翻页服务器面板
    :return:
    """
    sever = nezha_res.sever_info(tz_ad, tz_api, tz_id)
    if not sever:
        return ikb([[('🔙 - 冒险者面板', 'members'), ('❌ - 返回星港', 'back_start')]]), None
    d = []
    for i in sever:
        d.append([i['name'], f'server:{i["id"]}'])
    lines = array_chunk(d, 3)
    lines.append([[('🔙 - 冒险者面板', 'members'), ('❌ - 返回星港', 'back_start')]])
    # keyboard是键盘，a是sever
    return ikb(lines), sever


"""admins ↓"""

gm_ikb_content = ikb([[('⭕ 注册开关', 'open-menu'), ('🎟️ 注册码管理', 'cr_link')],
                      [('💊 查询用户', 'ch_link'), ('🏬 兑换设置', 'set_renew')],
                      [('👥 用户列表', 'normaluser'), ('👑 白名单用户', 'whitelist'), ('💠 设备列表', 'user_devices')],
                      [('🌏 定时任务', 'schedall'), ('🕹️ 返回主控台', 'back_start'), ('其他设置 🪟', 'back_config')]])


def open_menu_ikb(openstats, timingstats) -> InlineKeyboardMarkup:
    return ikb([[(f'{openstats} 开放注册', 'open_stat'), (f'{timingstats} 定时注册', 'open_timing')],
                [('🤖 注册天数设置', 'open_us'),('⭕ 注册总数限制', 'all_user_limit')], [('🌟 返回上一级', 'manage')]])


back_free_ikb = ikb([[('🔙 返回上一级', 'open-menu')]])
back_open_menu_ikb = ikb([[('🪪 重新设置定时', 'open_timing'), ('🔙 注册状态', 'open-menu')]])
re_cr_link_ikb = ikb([[('♻️ 继续生成', 'cr_link'), ('🎗️ 返回主控台', 'manage')]])
close_it_ikb = ikb([[('❌ - 湮灭', 'closeit')]])


def ch_link_ikb(ls: list) -> InlineKeyboardMarkup:
    lines = array_chunk(ls, 2)
    lines.append([["💫 返回主控台", "manage"]])
    return ikb(lines)


def date_ikb(i) -> InlineKeyboardMarkup:
    return ikb([[('🌘 - 月卡', f'register_mon_{i}'), ('🌗 - 季卡', f'register_sea_{i}'),
                 ('🌖 - 半年', f'register_half_{i}')],
                [('🌕 - 年卡', f'register_year_{i}'), ('🌑 - 未使用', f'register_unused_{i}'), ('🎟️ - 已使用', f'register_used_{i}')],
                [('🔙 - 返回', 'ch_link')]])

# 翻页按钮
async def cr_paginate(total_page: int, current_page: int, n) -> InlineKeyboardMarkup:
    """
    :param total_page: 总数
    :param current_page: 目前
    :param n: mode 可变项
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'pagination_keyboard:{number}' + f'_{n}')
    next = InlineButton('⏭️ 快进+5', f'users_iv:{current_page + 5}-{n}')
    previous = InlineButton('⏮️ 快退-5', f'users_iv:{current_page - 5}-{n}')
    followUp = [InlineButton('❌ 关闭', f'closeit')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard


async def users_iv_button(total_page: int, current_page: int, tg) -> InlineKeyboardMarkup:
    """
    :param total_page: 总页数
    :param current_page: 当前页数
    :param tg: 可操作的tg_id
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'users_iv:{number}' + f'_{tg}')
    next = InlineButton('⏭️ 快进+5', f'users_iv:{current_page + 5}_{tg}')
    previous = InlineButton('⏮️ 快退-5', f'users_iv:{current_page - 5}_{tg}')
    followUp = [InlineButton('❌ 关闭', f'closeit')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard


async def plays_list_button(total_page: int, current_page: int, days) -> InlineKeyboardMarkup:
    """
    :param total_page: 总页数
    :param current_page: 当前页数
    :param days: 请求获取多少天
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'uranks:{number}' + f'_{days}')
    # 添加按钮,前进5, 后退5
    next = InlineButton('⏭️ 快进+5', f'uranks:{current_page + 5}_{days}')
    previous = InlineButton('⏮️ 快退-5', f'uranks:{current_page - 5}_{days}')
    followUp = [InlineButton('❌ 关闭', 'closeit')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard


async def store_query_page(total_page: int, current_page: int) -> InlineKeyboardMarkup:
    """
    member的注册码查询分页
    :param total_page: 总
    :param current_page: 当前
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'store-query:{number}')
    next = InlineButton('⏭️ 快进+5', f'store-query:{current_page + 5}')
    previous = InlineButton('⏮️ 快退-5', f'store-query:{current_page - 5}')
    followUp = [InlineButton('🔙 返回', 'storeall')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard

async def whitelist_page_ikb(total_page: int, current_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'whitelist:{number}')
    next = InlineButton('⏭️ 快进+5', f'whitelist:{current_page + 5}')
    previous = InlineButton('⏮️ 快退-5', f'whitelist:{current_page - 5}')
    followUp = [InlineButton('🔙 返回', 'manage')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard
async def normaluser_page_ikb(total_page: int, current_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'normaluser:{number}')
    next = InlineButton('⏭️ 快进+5', f'normaluser:{current_page + 5}')
    previous = InlineButton('⏮️ 快退-5', f'normaluser:{current_page - 5}')
    followUp = [InlineButton('🔙 返回', 'manage')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard
def devices_page_ikb( has_prev: bool, has_next: bool, page: int) -> InlineKeyboardMarkup:
    # 构建分页按钮
    buttons = []
    if has_prev or has_next:
        nav_buttons = []
        if has_prev:
            nav_buttons.append(('⬅️', f'devices:{page-1}'))
        nav_buttons.append((f'第 {page} 页', 'none'))
        if has_next:
            nav_buttons.append(('➡️', f'devices:{page+1}'))
        buttons.append(nav_buttons)
    # 添加返回按钮
    buttons.append([('🔙 返回', 'manage')])
    keyboard = ikb(buttons)
    return keyboard
async def favorites_page_ikb(total_page: int, current_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboard()
    keyboard.paginate(total_page, current_page, 'page_my_favorites:{number}')
    next = InlineButton('⏭️ 快进+5', f'page_my_favorites:{current_page + 5}')
    previous = InlineButton('⏮️ 快退-5', f'page_my_favorites:{current_page - 5}')
    followUp = [InlineButton('🔙 返回', 'members')]
    if total_page > 5:
        if current_page - 5 >= 1:
            followUp.append(previous)
        if current_page + 5 < total_page:
            followUp.append(next)
    keyboard.row(*followUp)
    return keyboard
def cr_renew_ikb():
    checkin = '✔️' if _open.checkin else '❌'
    exchange = '✔️' if _open.exchange else '❌'
    whitelist = '✔️' if _open.whitelist else '❌'
    invite = '✔️' if _open.invite else '❌'
    # 添加邀请等级的显示
    invite_lv_text = {
        'a': '白名单用户',
        'b': '普通用户',
        'c': '已禁用账户',
        'd': '未注册用户'
    }.get(_open.invite_lv, '未知等级')
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(InlineButton(f'{checkin} 签到奖励', f'set_renew-checkin'),
                 InlineButton(f'{exchange} 自动续费', f'set_renew-exchange'),
                 InlineButton(f'{whitelist} 兑换白名单', f'set_renew-whitelist'),
                 InlineButton(f'{invite} 兑换注册码', f'set_renew-invite'),
                 InlineButton(f'注册码生成权限: {invite_lv_text}', f'set_invite_lv')
                 )
    keyboard.row(InlineButton(f'🫧 返回', 'manage'))
    return keyboard

def invite_lv_ikb():
    keyboard = ikb([
        [('🅰️ 白名单用户', 'set_invite_lv-a'), ('🅱️ 普通用户', 'set_invite_lv-b')],
        [('©️ 已禁用账户', 'set_invite_lv-c'), ('🅳️ 未注册用户', 'set_invite_lv-d')],
        [('🔙 返回', 'set_renew')]
    ])
    return keyboard

""" config_panel ↓"""


def config_preparation() -> InlineKeyboardMarkup:
    mp_set = '✅' if moviepilot.status else '❎'
    auto_up = '✅' if auto_update.status else '❎'
    leave_ban = '✅' if _open.leave_ban else '❎'
    uplays = '✅' if _open.uplays else '❎'
    fuxx_pt = '✅' if fuxx_pitao else '❎'
    red_envelope_status = '✅' if red_envelope.status else '❎'
    allow_private = '✅' if red_envelope.allow_private else '❎'
    keyboard = ikb(
        [[('📄 导出日志', 'log_out'), ('📌 设置探针', 'set_tz')],
         [('🎬 媒体库显隐', 'set_block'), (f'{fuxx_pt} 用户过滤', 'set_fuxx_pitao')],
         [('💠 普通线路设置', 'set_line'),('🌟 白名单线路设置', 'set_whitelist_line')],
         [(f'{leave_ban} 退群封禁', 'leave_ban'), (f'{uplays} 观影奖励', 'set_uplays')],
         [(f'{auto_up} 自动更新', 'set_update'), (f'{mp_set} 点播功能', 'set_mp')],
         [(f'{red_envelope_status} 红包功能', 'set_red_envelope_status'), (f'{allow_private} 专属红包', 'set_red_envelope_allow_private')],
         [(f'赠送天数设置({kk_gift_days}天)', 'set_kk_gift_days')],
         [('🔙 返回', 'manage')]])
    return keyboard


back_config_p_ikb = ikb([[("🎮  ️返回主控", "back_config")]])


def back_set_ikb(method) -> InlineKeyboardMarkup:
    return ikb([[("♻️ 重新设置", f"{method}"), ("🔙 返回主页", "back_config")]])


def try_set_buy(ls: list) -> InlineKeyboardMarkup:
    d = [[ls], [["✅ 体验结束返回", "back_config"]]]
    return ikb(d)

""" other """
register_code_ikb = ikb([[('🎟️ 签订星图契约', 'create'), ('❌ 湮灭', 'closeit')]])
dp_g_ikb = ikb([[("🌌 探索我的星域", "t.me/star_emby", "url")]])


async def cr_kk_ikb(uid, first):
    text = ''
    text1 = ''
    keyboard = []
    data = await members_info(uid)
    if data is None:
        text += f'**· 🆔 TG** ：[{first}](tg://user?id={uid}) [`{uid}`]\n数据库中没有此用户信息，用户尚未注册'
    else:
        name, lv, ex, us, embyid, pwd2 = data
        if name != '无账户信息':
            ban = "🌟 解除封禁" if lv == "**已禁用**" else '💢 封禁用户'
            keyboard = [[ban, f'user_ban-{uid}'], ['⚠️ 删除账户', f'closeemby-{uid}']]
            if len(extra_emby_libs) > 0:
                success, rep = emby.user(embyid=embyid)
                if success:
                    try:
                        currentblock = rep["Policy"]["BlockedMediaFolders"]
                    except KeyError:
                        currentblock = []
                    # 此处符号用于展示是否开启的状态
                    libs, embyextralib = ['✖️', f'embyextralib_unblock-{uid}'] if set(extra_emby_libs).issubset(
                        set(currentblock)) else ['✔️', f'embyextralib_block-{uid}']
                    keyboard.append([f'{libs} 额外媒体库', embyextralib])
            try:
                rst = await emby.emby_cust_commit(user_id=embyid, days=30)
                last_time = rst[0][0]
                toltime = rst[0][1]
                text1 = f"**· 🔋 最后活跃时间** | {last_time.split('.')[0]}\n" \
                        f"**· 📅 过去30天观看时长** | {toltime} 分钟"
            except (TypeError, IndexError, ValueError):
                text1 = f"**· 📅 过去30天无观看记录**"
        else:
            keyboard.append(['✨ 赠送账户', f'gift-{uid}'])
        text += f"**· 👤 用户档案**\n" \
                f"**· 📊 账户状态** | {lv}\n" \
                f"**· 🍥 余额** | {us}\n" \
                f"**· 💠 用户名** | {name}\n" \
                f"**· 🚨 到期时间** | **{ex}**\n"
        text += text1
        keyboard.extend([['🚫 踢出群组', f'fuckoff-{uid}'], ['❌ 关闭消息', f'closeit']])
        lines = array_chunk(keyboard, 2)
        keyboard = ikb(lines)
    return text, keyboard


def cv_user_playback_reporting(user_id):
    return ikb([[('🎬 播放记录', f'userip-{user_id}'), ('❌ 关闭面板', 'closeit')]])


def gog_rester_ikb(link=None) -> InlineKeyboardMarkup:
    link_ikb = ikb([[('🎁 领取星符', link, 'url')]]) if link else ikb([[('✨ 踏上星途', f't.me/{bot_name}', 'url')]])
    return link_ikb


""" sched_panel ↓"""


def sched_buttons():
    dayrank = '✅' if schedall.dayrank else '❎'
    weekrank = '✅' if schedall.weekrank else '❎'
    dayplayrank = '✅' if schedall.dayplayrank else '❎'
    weekplayrank = '✅' if schedall.weekplayrank else '❎'
    check_ex = '✅' if schedall.check_ex else '❎'
    low_activity = '✅' if schedall.low_activity else '❎'
    backup_db = '✅' if schedall.backup_db else '❎'
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(InlineButton(f'{dayrank} 日播放榜', f'sched-dayrank'),
                 InlineButton(f'{weekrank} 周播放榜', f'sched-weekrank'),
                 InlineButton(f'{dayplayrank} 日活跃榜', f'sched-dayplayrank'),
                 InlineButton(f'{weekplayrank} 周活跃榜', f'sched-weekplayrank'),
                 InlineButton(f'{check_ex} 到期处理', f'sched-check_ex'),
                 InlineButton(f'{low_activity} 低活跃处理', f'sched-low_activity'),
                 InlineButton(f'{backup_db} 数据库备份', f'sched-backup_db')
                 )
    keyboard.row(InlineButton(f'🫧 返回', 'manage'))
    return keyboard


""" checkin 按钮↓"""

# def shici_button(ls: list):
#     shici = []
#     for l in ls:
#         l = [l, f'checkin-{l}']
#         shici.append(l)
#     # print(shici)
#     lines = array_chunk(shici, 4)
#     return ikb(lines)


# checkin_button = ikb([[('🔋 重新签到', 'checkin'), ('🎮 返回主页', 'back_start')]])

""" Request_media """

# request_tips_ikb = ikb([[('✔️ 已转向私聊求片', 'go_to_qiupian')]])

request_tips_ikb = None


def get_resource_ikb(download_name: str):
    # 翻页 + 下载此片 + 取消操作
    return ikb([[(f'锁定星图目标', f'download_{download_name}'), ('激活星图订阅', f'submit_{download_name}')],
                [('❌ 湮灭', 'closeit')]])
re_download_center_ikb = ikb([
    [('🍿 星域点播', 'get_resource'), ('📶 星尘传输进度', 'download_rate')],
    [('🔙 返回', 'members')]])
continue_search_ikb = ikb([
    [('🔄 继续探索星海', 'continue_search'), ('❌ 中止探索', 'cancel_search')],
    [('🔙 返回', 'download_center')]
])
def download_resource_ids_ikb(resource_ids: list):
    buttons = []
    row = []
    for i in range(0, len(resource_ids), 2):
        current_id = resource_ids[i]
        current_button = [f"星图目标编号: {current_id}", f'download_resource_id_{current_id}']
        if i + 1 < len(resource_ids):
            next_id = resource_ids[i + 1]
            next_button = [f"星图目标编号: {next_id}", f'download_resource_id_{next_id}']
            row.append([current_button, next_button])
        else:
            row.append([current_button])
    buttons.extend(row)
    buttons.append([('❌ 中止星尘传输', 'cancel_download')])
    return ikb(buttons)
def request_record_page_ikb(has_prev: bool, has_next: bool):
    buttons = []
    if has_prev:
        buttons.append(('< 上一星页', 'request_record_prev'))
    if has_next:
        buttons.append(('下一星页 >', 'request_record_next'))
    return ikb([buttons, [('🔙 返回', 'download_center')]])
def mp_search_page_ikb(has_prev: bool, has_next: bool, page: int):
    buttons = []
    if has_prev:
        buttons.append(('< 上一星页', 'mp_search_prev_page'))
    if has_next:
        buttons.append(('下一星页 >', 'mp_search_next_page'))
    return ikb([buttons, [('💾 锁定目标', 'mp_search_select_download'), ('❌ 中止探索', 'cancel_search')]])

# 添加 MoviePilot 设置按钮
def mp_config_ikb():
    """MoviePilot 设置面板按钮"""
    mp_status = '✅' if moviepilot.status else '❎'
    lv_text = '无'
    if moviepilot.lv == 'a':
        lv_text = '白名单用户'
    elif moviepilot.lv == 'b':
        lv_text = '普通用户'
    keyboard = ikb([
        [(f'{mp_status} 点播功能开关', 'set_mp_status')],
        [('💰 设置点播价格', 'set_mp_price'), ('👥 设置权限等级', 'set_mp_lv')],
        [('📝 设置日志频道', 'set_mp_log_channel')],
        [('🔙 返回', 'back_config')]
    ])
    return keyboard