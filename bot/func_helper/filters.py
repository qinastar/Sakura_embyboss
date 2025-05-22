#!/usr/bin/python3
from pyrogram.errors import BadRequest, PeerIdInvalid
from pyrogram.filters import create
from bot import admins, owner, group, LOGGER
from pyrogram.enums import ChatMemberStatus


# async def owner_filter(client, update):
#     """
#     过滤 owner
#     :param client:
#     :param update:
#     :return:
#     """
#     user = update.from_user or update.sender_chat
#     uid = user.id
#     return uid == owner

# 三个参数给on用
async def admins_on_filter(filt, client, update) -> bool:
    """
    过滤admins中id，包括owner
    :param client:
    :param update:
    :return:
    """
    user = update.from_user or update.sender_chat
    uid = user.id
    return bool(uid == owner or uid in admins or uid in group)


async def admins_filter(update):
    """
    过滤admins中id，包括owner
    """
    user = update.from_user or update.sender_chat
    uid = user.id
    return bool(uid == owner or uid in admins)


async def user_in_group_filter(client, update):
    """
    过滤在授权组中的人员
    :param client:
    :param update:
    :return:
    """
    uid = update.from_user or update.sender_chat
    uid = uid.id
    for i in group:
        try:
            chat_id_to_check = int(i)
            u = await client.get_chat_member(chat_id=chat_id_to_check, user_id=uid)
            if u.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER]:
                return True
        except PeerIdInvalid:
            LOGGER.error(f"配置的群组ID {i} 无效。请检查配置。")
            continue
        except ValueError:
            LOGGER.error(f"配置的群组ID {i} 格式不正确，无法转换为整数。请检查配置。")
            continue
        except BadRequest as e:
            if e.ID == 'USER_NOT_PARTICIPANT':
                pass
            elif e.ID == 'CHAT_ADMIN_REQUIRED':
                LOGGER.error(f"Bot不能在 {i} 中工作，请检查bot是否在群组及其权限设置")
            else:
                LOGGER.error(f"检查群组 {i} 成员时发生 BadRequest: {e}")
            continue
    return False


async def user_in_group_on_filter(filt, client, update):
    """
    过滤在授权组中的人员
    :param client:
    :param update:
    :return:
    """
    uid = update.from_user or update.sender_chat
    uid = uid.id
    for i in group:
        try:
            chat_id_to_check = int(i)
            u = await client.get_chat_member(chat_id=chat_id_to_check, user_id=uid)
            if u.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER,
                            ChatMemberStatus.OWNER]:
                return True
        except PeerIdInvalid:
            LOGGER.error(f"配置的群组ID {i} 无效。请检查配置 (on_filter)。")
            continue
        except ValueError:
            LOGGER.error(f"配置的群组ID {i} 格式不正确，无法转换为整数。请检查配置 (on_filter)。")
            continue
        except BadRequest as e:
            if e.ID == 'USER_NOT_PARTICIPANT':
                pass
            elif e.ID == 'CHAT_ADMIN_REQUIRED':
                LOGGER.error(f"Bot不能在 {i} 中工作，请检查bot是否在群组及其权限设置 (on_filter)")
            else:
                LOGGER.error(f"检查群组 {i} 成员时发生 BadRequest (on_filter): {e}")
            continue
    return False


# 过滤 on_message or on_callback 的admin
admins_on_filter = create(admins_on_filter)
admins_filter = create(admins_filter)

# 过滤 是否在群内
user_in_group_f = create(user_in_group_filter)
user_in_group_on_filter = create(user_in_group_on_filter)
