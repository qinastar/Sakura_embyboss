"""
服务器讯息打印

"""
from datetime import datetime, timezone, timedelta
from pyrogram import filters
from bot import bot, emby_line, emby_whitelist_line, forward
from bot.func_helper.emby import emby
from bot.func_helper.filters import user_in_group_on_filter
from bot.sql_helper.sql_emby import sql_get_emby
from bot.func_helper.fix_bottons import cr_page_server
from bot.func_helper.msg_utils import callAnswer, editMessage


@bot.on_callback_query(filters.regex('server') & user_in_group_on_filter)
async def server(_, call):
    data = sql_get_emby(tg=call.from_user.id)
    if not data:
        return await editMessage(call, '⚠️ 数据库没有你，请重新 /start录入')
    await callAnswer(call, '🌐查询中...')
    try:
        j = int(call.data.split(':')[1])
    except IndexError:
        # 第一次查看
        send = await editMessage(call, "**▎🌐查询中...\n\nο(=•ω＜=)ρ⌒☆ 发送bibo电波~bibo~ \n⚡ 点击按钮查看相应服务器状态**")
        if send is False:
            return

        keyboard, sever = await cr_page_server()
        server_info = sever[0]['server'] if sever == '' else ''
    else:
        keyboard, sever = await cr_page_server()
        server_info = ''.join([item['server'] for item in sever if item['id'] == j])

    pwd = '空' if not data.pwd else data.pwd
    line = ''
    if data.lv == 'b':
        line = f'{emby_line}'
    elif data.lv == 'a':
        line = f'{emby_line}'
        if emby_whitelist_line:
            line += f'\n{emby_whitelist_line}'
    else:
        line = ' - **无权查看**'
    try:
        online = emby.get_current_playing_count()
    except:
        online = 'Emby服务器断连 ·0'
    text = f'**▎↓目前线路 & 用户密码：**`{pwd}`\n' \
           f'{line}\n\n' \
           f'{server_info}' \
           f'· 🎬 在线 | **{online}** 人\n\n' \
           f'**· 🌏 [{(datetime.now(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M:%S")}]**'
    await editMessage(call, text, buttons=keyboard)



@bot.on_callback_query(filters.regex('forward_help') & user_in_group_on_filter)
async def forward_help(_, call):
    """显示Forward使用帮助"""
    await callAnswer(call, '📱 详细使用方法已显示在消息中')
    
    help_text = f'**📱 Forward 使用帮助**\n\n' \
                f'**什么是Forward？**\n' \
                f'Forward是iOS平台上的一个优秀的Emby/Jellyfin客户端\n\n' \
                f'**使用步骤：**\n' \
                f'1. 在App Store下载安装Forward应用\n' \
                f'2. 点击上方的forward://链接会自动复制\n' \
                f'3. 打开Safari浏览器\n' \
                f'4. 在地址栏粘贴链接并访问\n' \
                f'5. 系统会提示跳转到Forward应用\n' \
                f'6. 确认跳转，服务器信息会自动导入\n\n' \
                f'**注意事项：**\n' \
                f'• 必须使用Safari浏览器打开链接\n' \
                f'• 确保Forward应用已安装\n' \
                f'• 链接包含您的账号信息，请勿泄露给他人\n' \
                f'• 如果导入失败，请检查应用版本和网络连接'
    
    from pyromod.helpers import ikb
    keyboard = ikb([
        [('🔙 返回', 'forward_import')]
    ])
    
    await editMessage(call, help_text, buttons=keyboard)


@bot.on_callback_query(filters.regex('forward_import') & user_in_group_on_filter)
async def forward_import(_, call):
    """处理Forward导入功能"""
    data = sql_get_emby(tg=call.from_user.id)
    if not data:
        return await editMessage(call, '⚠️ 数据库没有你，请重新 /start录入')
    
    if not data.name or not data.pwd:
        return await editMessage(call, '⚠️ 你还没有Emby账号，请先创建账号')
    
    await callAnswer(call, '📱 正在生成Forward链接...')
    
    # 构建基本的Forward链接
    scheme = forward.scheme
    host = forward.host
    port = forward.port
    username = data.name
    password = data.pwd
    
    # 基本链接
    forward_link = f"forward://import?type=emby&scheme={scheme}&host={host}&port={port}&username={username}&password={password}"
    
    # 如果有多线路配置，添加多线路支持
    if forward.lines and len(forward.lines) > 0:
        forward_link += f"&title=Emby服务器"
        for i, line in enumerate(forward.lines, 1):
            forward_link += f"&line{i}={line.url}&line{i}title={line.title}"
    
    # 构建键盘
    from pyromod.helpers import ikb
    keyboard = ikb([
        [('📱 使用说明', 'forward_help')],
        [('🔙 返回', 'server')]
    ])
    
    text = f'**📱 Forward 快速导入**\n\n' \
           f'**Forward链接：**\n' \
           f'`{forward_link}`\n\n' \
           f'**使用方法：**\n' \
           f'1. 点击上方链接会自动复制\n' \
           f'2. 在Safari中粘贴并打开\n' \
           f'3. 会自动跳转到Forward应用导入\n\n' \
           f'**注意事项：**\n' \
           f'• 确保已安装Forward应用\n' \
           f'• 必须使用Safari浏览器打开\n' \
           f'• 链接包含您的账号信息，请妥善保管'
    
    await editMessage(call, text, buttons=keyboard)
