# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message
from .. import get_all_plugins


@userge.on_cmd("all", about="__list all plugins in plugins/ path__")
async def getplugins(message: Message):
    all_plugins = ['/'.join(i.split('.')) for i in get_all_plugins()]

    out_str = "**--All Userge Plugins--**\n\n"

    for plugin in all_plugins:
        out_str += f"    `{plugin}.py`\n"

    await message.edit(text=out_str, del_in=0)
