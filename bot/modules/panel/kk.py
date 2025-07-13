"""
kk - 星域守护者的管理面板
星图契约管理：赠予、禁用、回收
"""
import pyrogram
from pyrogram import filters
from pyrogram.errors import BadRequest
from bot import bot, prefixes, owner, admins, LOGGER, extra_emby_libs, config
from bot.func_helper.emby import emby
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.fix_bottons import cr_kk_ikb, gog_rester_ikb
from bot.func_helper.msg_utils import deleteMessage, sendMessage, editMessage
from bot.func_helper.utils import judge_admins, cr_link_two, tem_deluser
from bot.sql_helper.sql_emby import sql_add_emby, sql_get_emby, sql_update_emby, Emby


# 管理用户
@bot.on_message(filters.command('kk', prefixes) & admins_on_filter)
async def user_info(_, msg):
    await deleteMessage(msg)
    if msg.reply_to_message is None:
        try:
            uid = int(msg.command[1])
            if not msg.sender_chat:
                if msg.from_user.id != owner and uid == owner:
                    return await sendMessage(msg, "⭕ 星域守护者，你无权查看星域主宰的信息", timer=60)
            else:
                pass
            first = await bot.get_chat(uid)
        except (IndexError, KeyError, ValueError):
            return await sendMessage(msg, '**请先为我指明一位星际旅者！**\n\n用法：/kk [tg_id]\n或者对某位冒险者回复kk', timer=60)
        except BadRequest:
            return await sendMessage(msg, f'{msg.command[1]} - 🎂抱歉，此星际旅者尚未踏入星域，或者星图坐标有误', timer=60)
        except AttributeError:
            pass
        else:
            sql_add_emby(uid)
            text, keyboard = await cr_kk_ikb(uid, first.first_name)
            await sendMessage(msg, text=text, buttons=keyboard)

    else:
        uid = msg.reply_to_message.from_user.id
        try:
            if msg.from_user.id != owner and uid == owner:
                return await msg.reply("⭕ 星域守护者，你无权查看星域主宰的信息")
        except AttributeError:
            pass

        sql_add_emby(uid)
        text, keyboard = await cr_kk_ikb(uid, msg.reply_to_message.from_user.first_name)
        await sendMessage(msg, text=text, buttons=keyboard)


# 封禁或者解除
@bot.on_callback_query(filters.regex('user_ban'))
async def kk_user_ban(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("星灵提醒：你没有执行此操作的权限", show_alert=True)

    await call.answer("✨ 星灵正在执行...")
    b = int(call.data.split("-")[1])
    if b in admins and b != call.from_user.id:
        return await editMessage(call, "⚠️ 星灵无权对其他星域守护者执行此操作", timer=60)

    first = await bot.get_chat(b)
    e = sql_get_emby(tg=b)
    if e.embyid is None:
        await editMessage(call, '💫 此星际旅者尚未获得星图契约。', timer=60)
    else:
        text = f'🌟 一位神秘的星域守护者对星际旅者的星图契约'
        if e.lv != "c":
            if await emby.emby_change_policy(id=e.embyid, method=True) is True:
                if sql_update_emby(Emby.tg == b, lv='c') is True:
                    text += f'施加了封印，此状态将持续到下次星图更新'
                    LOGGER.info(text)
                else:
                    text += '封印失败，星图数据记录出现波动'
                    LOGGER.error(text)
            else:
                text += f'封印失败，星图服务器无响应'
                LOGGER.error(text)
        elif e.lv == "c":
            if await emby.emby_change_policy(id=e.embyid):
                if sql_update_emby(Emby.tg == b, lv='b'):
                    text += '的封印已被解除'
                    LOGGER.info(text)
                else:
                    text += '解除封印失败，星图数据记录出现波动'
                    LOGGER.error(text)
            else:
                text += '解除封印失败，星图服务器无响应'
                LOGGER.error(text)
        await editMessage(call, text)
        await bot.send_message(b, text)


# 开通额外媒体库
@bot.on_callback_query(filters.regex('embyextralib_unblock'))
async def user_embyextralib_unblock(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("请不要以下犯上 ok？", show_alert=True)
    await call.answer(f'🎬 正在为TA开启显示ing')
    tgid = int(call.data.split("-")[1])
    e = sql_get_emby(tg=tgid)
    if e.embyid is None:
        await editMessage(call, f'💢 ta 没有注册账户。', timer=60)
    embyid = e.embyid
    success, rep = emby.user(embyid=embyid)
    currentblock = []
    if success:
        try:
            currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
            # 保留不同的元素
            currentblock = [x for x in currentblock if x not in extra_emby_libs] + [x for x in extra_emby_libs if
                                                                                    x not in currentblock]
        except KeyError:
            currentblock = ["播放列表"]
        re = await emby.emby_block(embyid, 0, block=currentblock)
        if re is True:
            await editMessage(call, f'🌟 好的，管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n'
                                    f'已开启了 [TA](tg://user?id={tgid}) 的额外媒体库权限\n{extra_emby_libs}')
        else:
            await editMessage(call,
                              f'🌧️ Error！管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n操作失败请检查设置！')


# 隐藏额外媒体库
@bot.on_callback_query(filters.regex('embyextralib_block'))
async def user_embyextralib_block(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("请不要以下犯上 ok？", show_alert=True)
    await call.answer(f'🎬 正在为TA关闭显示ing')
    tgid = int(call.data.split("-")[1])
    e = sql_get_emby(tg=tgid)
    if e.embyid is None:
        await editMessage(call, f'💢 ta 没有注册账户。', timer=60)
    embyid = e.embyid
    success, rep = emby.user(embyid=embyid)
    currentblock = []
    if success:
        try:
            currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
            currentblock = list(set(currentblock + extra_emby_libs))
        except KeyError:
            currentblock = ["播放列表"] + extra_emby_libs
        re = await emby.emby_block(embyid, 0, block=currentblock)
        if re is True:
            await editMessage(call, f'🌟 好的，管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n'
                                    f'已关闭了 [TA](tg://user?id={tgid}) 的额外媒体库权限\n{extra_emby_libs}')
        else:
            await editMessage(call,
                              f'🌧️ Error！管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n操作失败请检查设置！')


# 赠送资格
@bot.on_callback_query(filters.regex('gift'))
async def gift(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("星灵提醒：你没有执行此操作的权限", show_alert=True)

    await call.answer("✨ 星灵正在执行...")
    b = int(call.data.split("-")[1])
    if b in admins and b != call.from_user.id:
        return await editMessage(call, "⚠️ 星灵无权对其他星域守护者执行此操作")

    first = await bot.get_chat(b)
    e = sql_get_emby(tg=b)
    if e.embyid is None:
        link = await cr_link_two(tg=call.from_user.id, for_tg=b, days=config.kk_gift_days)
        await editMessage(call, f"🌟 一位神秘的星域守护者为这位星际旅者赠予了星图契约资格。\n请前往星灵完成契约签订：",
                          buttons=gog_rester_ikb(link))
        LOGGER.info(f"【星域守护者】已为冒险者 {b} 赠予星图契约资格")
    else:
        await editMessage(call, '💫 此星际旅者已持有星图契约。')


# 删除账户
@bot.on_callback_query(filters.regex('closeemby'))
async def close_emby(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("星灵提醒：你没有执行此操作的权限", show_alert=True)

    await call.answer("✨ 星灵正在执行...")
    b = int(call.data.split("-")[1])
    if b in admins and b != call.from_user.id:
        return await editMessage(call, "⚠️ 星灵无权对其他星域守护者执行此操作", timer=60)

    first = await bot.get_chat(b)
    e = sql_get_emby(tg=b)
    if e.embyid is None:
        return await editMessage(call, '💫 此星际旅者尚未获得星图契约。', timer=60)

    if await emby.emby_del(e.embyid):
        sql_update_emby(Emby.embyid == e.embyid, embyid=None, name=None, pwd=None, pwd2=None, lv='d', cr=None, ex=None)
        tem_deluser()
        await editMessage(call,
                          f'🌟 星图契约已被回收\n等级：{e.lv} - 契约者 {e.name} 的星图印记已消散。')
        await bot.send_message(b, f"⚠️ 你的星图契约已被一位神秘的星域守护者收回，契约者身份 {e.name} 的星图印记已消散")
        LOGGER.info(f"【星域守护者】{call.from_user.id} 已回收冒险者 {b} 的星图契约 {e.name}")
    else:
        await editMessage(call, f'⚠️ 星图契约回收失败\n等级：{e.lv} - 契约者 {e.name} 的星图印记未能消散。')
        LOGGER.info(f"【星域守护者】{call.from_user.id} 回收冒险者 {b} 的星图契约 {e.name} 失败")


@bot.on_callback_query(filters.regex('fuckoff'))
async def fuck_off_m(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("星灵提醒：你没有执行此操作的权限", show_alert=True)

    await call.answer("✨ 星灵正在执行...")
    user_id = int(call.data.split("-")[1])
    if user_id in admins and user_id != call.from_user.id:
        return await editMessage(call, "⚠️ 星灵无权对其他星域守护者执行此操作", timer=60)
    try:
        user = await bot.get_chat(user_id)
        await call.message.chat.ban_member(user_id)
        await editMessage(call, f'🌠 一位星际旅者已迷失在星海中...')
        LOGGER.info(f"【星域守护者】{call.from_user.id} 已将冒险者 {user_id} 驱逐出星域 {call.message.chat.id}")
    except pyrogram.errors.ChatAdminRequired:
        await editMessage(call, "⚠️ 星灵需要更高的权限才能执行此操作")
    except pyrogram.errors.UserAdminInvalid:
        await editMessage(call, "⚠️ 星灵无权对星域管理者执行此操作")
