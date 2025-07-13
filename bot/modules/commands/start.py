"""
启动面板start命令 返回面ban

+ myinfo 个人数据
+ count  服务器媒体数
"""
import asyncio
from pyrogram import filters

from bot.func_helper.emby import Embyservice
from bot.func_helper.utils import judge_admins, members_info, open_check
from bot.modules.commands.exchange import rgs_code
from bot.sql_helper.sql_emby import sql_add_emby
from bot.func_helper.filters import user_in_group_filter, user_in_group_on_filter
from bot.func_helper.msg_utils import deleteMessage, sendMessage, sendPhoto, callAnswer, editMessage
from bot.func_helper.fix_bottons import group_f, judge_start_ikb, judge_group_ikb, cr_kk_ikb
from bot.modules.extra import user_cha_ip
from bot import bot, prefixes, group, bot_photo, ranks, sakura_b


# 反命令提示
@bot.on_message((filters.command('start', prefixes) | filters.command('count', prefixes)) & filters.chat(group))
async def ui_g_command(_, msg):
    await asyncio.gather(deleteMessage(msg),
                         sendMessage(msg,
                                     f"(｡♥‿♥｡) 亲爱的主人～这个指令需要私聊星灵才能使用哦！\n\n✨ 请点击机器人头像或发送 /start 开始你的星际冒险吧！",
                                     buttons=group_f, timer=60))


# 查看自己的信息
@bot.on_message(filters.command('myinfo', prefixes) & user_in_group_on_filter)
async def my_info(_, msg):
    await msg.delete()
    if msg.sender_chat:
        return
    text, keyboard = await cr_kk_ikb(uid=msg.from_user.id, first=msg.from_user.first_name)
    await sendMessage(msg, text, timer=60)


@bot.on_message(filters.command('count', prefixes) & user_in_group_on_filter & filters.private)
async def count_info(_, msg):
    await deleteMessage(msg)
    text = Embyservice.get_medias_count()
    await sendMessage(msg, text, timer=60)


# 私聊开启面板
@bot.on_message(filters.command('start', prefixes) & filters.private)
async def p_start(_, msg):
    if not await user_in_group_filter(_, msg):
        return await asyncio.gather(deleteMessage(msg),
                                    sendMessage(msg,
                                                '(╥﹏╥) 呜呜呜～检测到你还没有加入我们的星际大家庭！\n\n💖 **需要先做这些才能使用星灵服务哦：**\n'
                                                '🌟 1. 加入我们的 **群组** (日常交流)\n'
                                                '🌟 2. 关注我们的 **频道** (重要通知)\n\n'
                                                '✨ 加入后再来找星灵，我会为你开启专属的星际账户～(๑•̀ㅂ•́)و✧',
                                                buttons=judge_group_ikb))
    try:
        u = msg.command[1].split('-')[0]
        if u == 'userip':
            name = msg.command[1].split('-')[1]
            if judge_admins(msg.from_user.id):
                return await user_cha_ip(_, msg, name)
            else:
                return await sendMessage(msg, '(｡>﹏<｡) 呀～你不是管理员，无法使用此指令哦！')
        if u in f'{ranks.logo}' or u == str(msg.from_user.id):
            await asyncio.gather(msg.delete(), rgs_code(_, msg, register_code=msg.command[1]))
        else:
            await asyncio.gather(sendMessage(msg, '(´⊙ω⊙`) 咦？这个注册码好像有问题诶～\n\n请检查是不是从官方渠道获取的正确星符哦！'), msg.delete())
    except (IndexError, TypeError):
        data = await members_info(tg=msg.from_user.id)
        is_admin = judge_admins(msg.from_user.id)
        if not data:
            sql_add_emby(msg.from_user.id)
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo,
                                           f"**✨ 初次相遇，命运的星光开始闪耀～**\n\n"
                                           f"(◕‿◕)♡ **你好呀，新的冒险者！**\n\n"
                                           f"🌟 星灵已为你创建专属档案，星际旅程即将开始！\n"
                                           f"💫 请再次发送 /start 来打开你的冒险者面板吧～"))
            return
        name, lv, ex, us, embyid, pwd2 = data
        stat, all_user, tem, timing = await open_check()
        text = (f"✧٩(ˊωˋ*)و✧ **星灵控制中心**\n\n"
               f"**🆔 冒险者编号** | `{msg.from_user.id}`\n" \
               f"**⭐ 当前星级** | {lv}\n"
               f"**💰 星尘余额** | {us}\n"
               f"**🎪 注册状态** | {stat}\n"
               f"**👥 总席位数** | {all_user}\n"
               f"**🎫 剩余席位** | {all_user - tem}\n")
        if not embyid:
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo, caption=text, buttons=judge_start_ikb(is_admin, False)))
        else:
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo,
                                           f"**✨ 星灵感应到了熟悉的气息～**\n\n(｡♥‿♥｡) **欢迎回来，我的冒险者！**\n\n💖 请选择你想要的星灵服务吧～",
                                           buttons=judge_start_ikb(is_admin, True)))


# 返回面板
@bot.on_callback_query(filters.regex('back_start'))
async def b_start(_, call):
    if await user_in_group_filter(_, call):
        is_admin = judge_admins(call.from_user.id)
        await asyncio.gather(callAnswer(call, "⭐ 返回星港"),
                             editMessage(call,
                                         text=f"**✨ 星灵感应到了熟悉的气息～**\n\n(｡♥‿♥｡) **欢迎回来，我的冒险者！**\n\n💖 请选择你想要的星灵服务吧～",
                                         buttons=judge_start_ikb(is_admin, account=True)))
    elif not await user_in_group_filter(_, call):
        await asyncio.gather(callAnswer(call, "⭐ 返回星港"),
                             editMessage(call, text='(╥﹏╥) 呜呜呜～检测到你还没有加入我们的星际大家庭！\n\n💖 **需要先做这些才能使用星灵服务哦：**\n'
                                                  '🌟 1. 加入我们的 **群组** (日常交流)\n'
                                                  '🌟 2. 关注我们的 **频道** (重要通知)\n\n'
                                                  '✨ 加入后再来找星灵，我会为你开启专属的星际账户～(๑•̀ㅂ•́)و✧',
                                         buttons=judge_group_ikb))


@bot.on_callback_query(filters.regex('store_all'))
async def store_alls(_, call):
    if not await user_in_group_filter(_, call):
        await asyncio.gather(callAnswer(call, "⭐ 返回星港"),
                             deleteMessage(call), sendPhoto(call, bot_photo,
                                                            '(╥﹏╥) 呜呜呜～检测到你还没有加入我们的星际大家庭！\n\n💖 **需要先做这些才能使用星灵服务哦：**\n'
                                                            '🌟 1. 加入我们的 **群组** (日常交流)\n'
                                                            '🌟 2. 关注我们的 **频道** (重要通知)\n\n'
                                                            '✨ 加入后再来找星灵，我会为你开启专属的星际账户～(๑•̀ㅂ•́)و✧',
                                                            judge_group_ikb))
    elif await user_in_group_filter(_, call):
        await callAnswer(call, '⭕ 星灵正在施法中...', True)
