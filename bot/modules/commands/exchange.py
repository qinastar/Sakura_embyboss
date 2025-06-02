"""
兑换注册码exchange
"""
from datetime import timedelta, datetime

from bot import bot, _open, LOGGER, bot_photo
from bot.func_helper.emby import emby
from bot.func_helper.fix_bottons import register_code_ikb
from bot.func_helper.msg_utils import sendMessage, sendPhoto
from bot.sql_helper.sql_code import Code
from bot.sql_helper.sql_emby import sql_get_emby, Emby
from bot.sql_helper import Session


def is_renew_code(input_string):
    if "Renew" in input_string:
        return True
    else:
        return False


async def rgs_code(_, msg, register_code):
    if _open.stat: return await sendMessage(msg, "🌟 星门大开，自由注册时刻，星符暂时失去魔力啦~")

    data = sql_get_emby(tg=msg.from_user.id)
    if not data: return await sendMessage(msg, "出错了，星门暂未为你开启，请先 /start")
    embyid = data.embyid
    ex = data.ex
    lv = data.lv
    if embyid:
        if not is_renew_code(register_code): return await sendMessage(msg,
                                                                      "🔔 很遗憾，你手中的并非续期星符，无法解锁星辰续航之力~",
                                                                      timer=60)
        with Session() as session:
            # with_for_update 是一个排他锁，其实就不需要悲观锁或者是乐观锁，先锁定先到的数据使其他session无法读取，修改(单独似乎不起作用，也许是不能完全防止并发冲突，于是加入原子操作)
            r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
            if not r: return await sendMessage(msg, "⛔ 你输入的续期星符似乎迷失在宇宙，请检查后再试~", timer=60)
            re = session.query(Code).filter(Code.code == register_code, Code.used.is_(None)).with_for_update().update(
                {Code.used: msg.from_user.id, Code.usedtime: datetime.now()})
            session.commit()  # 必要的提交。否则失效
            tg1 = r.tg
            us1 = r.us
            used = r.used
            if re == 0: return await sendMessage(msg,
                                                 f'这枚 `{register_code}` \n续期星符已被神秘旅者使用，星门只为勇者敞开~')
            session.query(Code).filter(Code.code == register_code).with_for_update().update(
                {Code.used: msg.from_user.id, Code.usedtime: datetime.now()})
            first = await bot.get_chat(tg1)
            # 此处需要写一个判断 now和ex的大小比较。进行日期加减。
            ex_new = datetime.now()
            if ex_new > ex:
                ex_new = ex_new + timedelta(days=us1)
                await emby.emby_change_policy(id=embyid, method=False)
                if lv == 'c':
                    session.query(Emby).filter(Emby.tg == msg.from_user.id).update({Emby.ex: ex_new, Emby.lv: 'b'})
                else:
                    session.query(Emby).filter(Emby.tg == msg.from_user.id).update({Emby.ex: ex_new})
                await sendMessage(msg, f'🎊 星际旅者，恭喜你，已获得 {us1} 天星辰续航！\n'
                                       f'✨ 你的冒险之旅已延长至：{ex_new.strftime("%Y-%m-%d %H:%M:%S")}', timer=60)
            elif ex_new < ex:
                ex_new = data.ex + timedelta(days=us1)
                session.query(Emby).filter(Emby.tg == msg.from_user.id).update({Emby.ex: ex_new})
                await sendMessage(msg,
                                  f'🎊 星际旅者，恭喜你，已收到一份来自神秘旅者的 {us1} 天🎁\n到期时间：{ex_new}__')
            session.commit()
            new_code = register_code[:-7] + "░" * 7
            await sendMessage(msg,
                              f'🌌 星门异动，光芒璀璨！一位无畏的星际旅者使用了续期星符，星门已为TA敞开新的宇宙旅程！\n'
                              f'愿星光指引TA前行，探索未知的星海！',
                              send=True)
            LOGGER.info(f"【续期码】：{msg.from_user.first_name}[{msg.chat.id}] 使用了 {register_code}，到期时间：{ex_new}")

    else:
        if is_renew_code(register_code): return await sendMessage(msg,
                                                                  "🔔 很遗憾，续期星符无法开启注册星门，请使用专属注册星符~",
                                                                  timer=60)
        if data.us > 0: return await sendMessage(msg, "✨ 星际旅者，你已拥有星图契约签订资格，请直接前往签订您的星图契约，勿重复使用星符哦~", timer=60)
        with Session() as session:
            # 我勒个豆，终于用 原子操作 + 排他锁 成功防止了并发更新
            # 在 UPDATE 语句中添加一个条件，只有当注册码未被使用时，才更新数据。这样，如果有两个用户同时尝试使用同一条注册码，只有一个用户的 UPDATE 语句会成功，因为另一个用户的 UPDATE 语句会发现注册码已经被使用。
            r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
            if not r: return await sendMessage(msg, "⛔ 你输入的注册星符似乎迷失在宇宙，请检查后再试~")
            re = session.query(Code).filter(Code.code == register_code, Code.used.is_(None)).with_for_update().update(
                {Code.used: msg.from_user.id, Code.usedtime: datetime.now()})
            session.commit()  # 必要的提交。否则失效
            tg1 = r.tg
            us1 = r.us
            used = r.used
            if re == 0: return await sendMessage(msg,
                                                 f'这枚 `{register_code}` \n注册星符已被神秘旅者激活，星门只为勇者敞开~')
            first = await bot.get_chat(tg1)
            x = data.us + us1
            session.query(Emby).filter(Emby.tg == msg.from_user.id).update({Emby.us: x})
            session.commit()
            await sendPhoto(msg, photo=bot_photo,
                            caption=f'🎊 星际旅者，恭喜你，已获得注册星门的资格！\n\n请选择你的命运之路~',
                            buttons=register_code_ikb)
            new_code = register_code[:-7] + "░" * 7
            await sendMessage(msg,
                              f'✨ **星门异动，光芒璀璨！**✨\n'
                              f'一位无畏的星际旅者使用了注册星符，星门已为TA敞开新的宇宙旅程！\n'
                              f'⭐ **愿星光指引TA前行，探索未知的星海！**⭐',
                              send=True)
            LOGGER.info(
                f"【注册码】：{msg.from_user.first_name}[{msg.chat.id}] 使用了 {register_code} - {us1}")

# @bot.on_message(filters.regex('exchange') & filters.private & user_in_group_on_filter)
# async def exchange_buttons(_, call):
#
#     await rgs_code(_, msg)
