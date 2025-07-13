"""
 一个群组检测，防止别人把bot拉过去，而刚好代码出现漏洞。
"""
import asyncio

from pyrogram import filters

from bot import bot, group, owner, LOGGER
from bot.func_helper.fix_bottons import dp_g_ikb

# 定义一个集合来存储已经处理过的群组的 id
processed_groups = set()


async def leave_bot(chat_id):
    await asyncio.sleep(30)
    try:
        # 踢出bot
        await bot.leave_chat(chat_id)
        LOGGER.info(f"bot已 退出未授权群聊【{chat_id}】")
    except Exception as e:
        # 记录异常信息
        LOGGER.error(e)


@bot.on_message(~filters.chat(group) & filters.group)
async def anti_use_bot(_, msg):
    if msg.chat.id in processed_groups:
        return
    else:
        processed_groups.add(msg.chat.id)
    if msg.from_user is not None:
        try:
            await bot.send_message(owner,
                                   f"🌌 一位神秘的冒险者({msg.from_user.id}) 尝试将星灵引入未认证的星域({msg.chat.id})，此举已被星灵察觉。")
            asyncio.create_task(leave_bot(msg.chat.id))
            await bot.send_message(msg.chat.id,
                                   f'❎ 这里并非星灵允许降临的星域！！！\n\n本星灵将在 **30s** 自动返回，如需指引前往已认证的星域，请联系星域守护者👇',
                                   reply_markup=dp_g_ikb)
            LOGGER.info(f"【一位冒险者({msg.from_user.id}) 尝试将星灵引入星域({msg.chat.id}) 被察觉】")
        except Exception as e:
            # 记录异常信息
            LOGGER.error(e)

    elif msg.from_user is None:
        try:
            await bot.send_message(chat_id=owner, text=f'🌌 一股未知力量 尝试将星灵引入未认证的星域({msg.chat.id})，此举已被星灵察觉。')
            asyncio.create_task(leave_bot(msg.chat.id))
            await bot.send_message(msg.chat.id,
                                   f'❎ 这里并非星灵允许降临的星域！！！\n\n本星灵将在 **30s** 自动返回，如需指引前往已认证的星域，请联系星域守护者👇',
                                   reply_markup=dp_g_ikb)
            LOGGER.info(f"【未知力量 尝试将星灵引入星域({msg.chat.id}) 被察觉】")
        except Exception as e:
            # 记录异常信息
            LOGGER.error(e)
