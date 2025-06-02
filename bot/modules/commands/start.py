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
                                     f"✨ 冒险者，这条指令需要通过星灵进行私密通讯哦~",
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
                                                '💢 冒险者，你的星图契约尚未激活！请先踏上星途加入我们的星际联盟（群组和频道），然后再次召唤星灵吧！\n\n⁉️ PS：若你已在星际联盟中却收到此消息，可能你的星图契约受到了未知力量的干扰，请联系星域守护者协助解除。',
                                                buttons=judge_group_ikb))
    try:
        u = msg.command[1].split('-')[0]
        if u == 'userip':
            name = msg.command[1].split('-')[1]
            if judge_admins(msg.from_user.id):
                return await user_cha_ip(_, msg, name)
            else:
                return await sendMessage(msg, '💢 你不是管理员，无法使用此命令')
        if u in f'{ranks.logo}' or u == str(msg.from_user.id):
            await asyncio.gather(msg.delete(), rgs_code(_, msg, register_code=msg.command[1]))
        else:
            await asyncio.gather(sendMessage(msg, '🤺 哎呀，这枚星符似乎无法解析呢？请检查是否来自星灵认可的渠道~'), msg.delete())
    except (IndexError, TypeError):
        data = await members_info(tg=msg.from_user.id)
        is_admin = judge_admins(msg.from_user.id)
        if not data:
            sql_add_emby(msg.from_user.id)
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo,
                                           f"**✨ 只有你想见星灵的时候我们的相遇才有意义**\n\n"
                                           f"🌌__你好鸭，神秘的冒险者！__\n\n"
                                           f"初次与星灵连接，星图信息已为你录入。\n"
                                           f"请再次召唤星灵面板吧 (/start)"))
            return
        name, lv, ex, us, embyid, pwd2 = data
        stat, all_user, tem, timing = await open_check()
        text = (f"🌌 __欢迎访问星灵终端！__\n\n"
               f"**· 🆔 用户のID** | `{msg.from_user.id}`\n" \
               f"**· 📊 星图契约状态** | {lv}\n"
               f"**· 🍒 星尘{sakura_b}** | {us}\n"
               f"**· ®️ 星门广纳状态** | {stat}\n"
               f"**· 🎫 星门契约上限** | {all_user}\n"
               f"**· 🎟️ 剩余星位** | {all_user - tem}\n")
        if not embyid:
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo, caption=text, buttons=judge_start_ikb(is_admin, False)))
        else:
            await asyncio.gather(deleteMessage(msg),
                                 sendPhoto(msg, bot_photo,
                                           f"**✨ 只有你想见星灵的时候我们的相遇才有意义**\n\n🌌__你好鸭，神秘的冒险者！请选择你的星灵服务__👇",
                                           buttons=judge_start_ikb(is_admin, True)))


# 返回面板
@bot.on_callback_query(filters.regex('back_start'))
async def b_start(_, call):
    if await user_in_group_filter(_, call):
        is_admin = judge_admins(call.from_user.id)
        await asyncio.gather(callAnswer(call, "⭐ 返回start"),
                             editMessage(call,
                                         text=f"**✨ 只有你想见星灵的时候我们的相遇才有意义**\n\n🌌__你好鸭，神秘的冒险者！请选择你的星灵服务__👇",
                                         buttons=judge_start_ikb(is_admin, account=True)))
    elif not await user_in_group_filter(_, call):
        await asyncio.gather(callAnswer(call, "⭐ 返回start"),
                             editMessage(call, text='💢 冒险者，你的星图契约尚未激活！请先踏上星途加入我们的星际联盟（群组和频道），然后再次召唤星灵吧！\n\n⁉️ PS：若你已在星际联盟中却收到此消息，可能你的星图契约受到了未知力量的干扰，请联系星域守护者协助解除。',
                                         buttons=judge_group_ikb))


@bot.on_callback_query(filters.regex('store_all'))
async def store_alls(_, call):
    if not await user_in_group_filter(_, call):
        await asyncio.gather(callAnswer(call, "⭐ 返回start"),
                             deleteMessage(call), sendPhoto(call, bot_photo,
                                                            '💢 冒险者，你的星图契约尚未激活！请先踏上星途加入我们的星际联盟（群组和频道），然后再次召唤星灵吧！',
                                                            judge_group_ikb))
    elif await user_in_group_filter(_, call):
        await callAnswer(call, '⭕ 正在编辑', True)
