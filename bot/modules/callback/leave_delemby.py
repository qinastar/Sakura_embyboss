from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

from bot import bot, group, LOGGER, _open
from bot.func_helper.utils import tem_deluser
from bot.sql_helper.sql_emby import sql_get_emby, sql_update_emby, Emby
from bot.func_helper.emby import emby


@bot.on_chat_member_updated(filters.chat(group))
async def leave_del_emby(_, event: ChatMemberUpdated):
    if event.old_chat_member and not event.new_chat_member:
        if not event.old_chat_member.is_member and event.old_chat_member.user:
            user_id = event.old_chat_member.user.id
            user_fname = event.old_chat_member.user.first_name
            try:
                e = sql_get_emby(tg=user_id)
                if e is None or e.embyid is None:
                    return
                if await emby.emby_del(id=e.embyid):
                    sql_update_emby(Emby.embyid == e.embyid, embyid=None, name=None, pwd=None, pwd2=None, lv='d', cr=None, ex=None)
                    tem_deluser()
                    LOGGER.info(
                        f'【退群删号】- 一位冒险者({user_id}) 已经离开了群组，其星图印记已消散！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'🌌 一位冒险者的星光黯淡了，其在星图上的印记也随之消散。')
                else:
                    LOGGER.error(
                        f'【退群删号】- 一位冒险者({user_id}) 已经离开了群组，但其星图印记未能消散，请星域守护者检查！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'🌌 一位冒险者的星光黯淡了，但其星图印记似乎受到了神秘力量的保护，未能完全消散，星域守护者请留意。')
                if _open.leave_ban:
                    await bot.ban_chat_member(chat_id=event.chat.id, user_id=user_id)
            except Exception as e:
                LOGGER.error(f"【退群删号】- {user_id}: {e}")
            else:
                pass
    elif event.old_chat_member and event.new_chat_member:
        if event.new_chat_member.status is ChatMemberStatus.BANNED:
            # print(2)
            user_id = event.new_chat_member.user.id
            user_fname = event.new_chat_member.user.first_name
            try:
                e = sql_get_emby(tg=user_id)
                if e is None or e.embyid is None:
                    return
                if await emby.emby_del(id=e.embyid):
                    sql_update_emby(Emby.embyid == e.embyid, embyid=None, name=None, pwd=None, pwd2=None, lv='d', cr=None,
                                    ex=None)
                    tem_deluser()
                    LOGGER.info(
                        f'【退群删号】- 一位冒险者({user_id}) 已经离开了群组，其星图印记已消散！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'🌌 一位冒险者的星光黯淡了，其在星图上的印记也随之消散。')
                else:
                    LOGGER.error(
                        f'【退群删号】- 一位冒险者({user_id}) 已经离开了群组，但其星图印记未能消散，请星域守护者检查！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'🌌 一位冒险者的星光黯淡了，但其星图印记似乎受到了神秘力量的保护，未能完全消散，星域守护者请留意。')
                if _open.leave_ban:
                    await bot.ban_chat_member(chat_id=event.chat.id, user_id=user_id)
            except Exception as e:
                LOGGER.error(f"【退群删号】- {user_id}: {e}")
            else:
                pass
