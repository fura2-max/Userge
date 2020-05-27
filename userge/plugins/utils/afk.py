# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import time
import asyncio
from random import choice, randint

from userge import userge, Message, Filters, Config, get_collection
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
REASON = ''
TIME = 0
USERS = {}

__tmp__ = SAVED_SETTINGS.find_one({'_id': 'AFK'})

if __tmp__:
    IS_AFK = __tmp__['on']
    REASON = __tmp__['data']
    TIME = __tmp__['time'] if 'time' in __tmp__ else 0

del __tmp__

for _user in AFK_COLLECTION.find():
    USERS.update({_user['_id']:  [_user['pcount'], _user['gcount'], _user['men']]})

IS_AFK_FILTER = Filters.create(lambda _, __: bool(IS_AFK))


@userge.on_cmd("afk", about={
    'header': "Set to AFK mode",
    'description': "Sets your status as AFK. Responds to anyone who tags/PM's.\n"
                   "you telling you are AFK. Switches off AFK when you type back anything.",
    'usage': "{tr}afk or {tr}afk [reason]"})
async def active_afk(message: Message):
    global REASON, IS_AFK, TIME
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    await CHANNEL.log(f"You went AFK! : `{REASON}`")
    await message.edit("`You went AFK!`", del_in=1)
    AFK_COLLECTION.drop()
    SAVED_SETTINGS.update_one(
        {'_id': 'AFK'}, {"$set": {'on': True, 'data': REASON, 'time': TIME}}, upsert=True)


@userge.on_filters(IS_AFK_FILTER & ~Filters.me & ~Filters.bot & (Filters.mentioned | \
    (Filters.private & ~Filters.service & Config.ALLOWED_CHATS)))
async def handle_afk_incomming(message: Message):
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await userge.get_user_dict(user_id)
    afk_time = time_formatter(round(time.time() - TIME))
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            if REASON:
                out_str = f"I'm still **AFK**.\nReason: `{REASON}`\nLast Seen: `{afk_time} ago`"
            else:
                out_str = choice(AFK_REASONS)
            await message.reply(out_str)
        if chat.type == 'private':
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        if REASON:
            out_str = f"I'm **AFK** right now.\nReason: `{REASON}`\nLast Seen: `{afk_time} ago`"
        else:
            out_str = choice(AFK_REASONS)
        await message.reply(out_str)
        if chat.type == 'private':
            USERS[user_id] = [1, 0, user_dict['mention']]
        else:
            USERS[user_id] = [0, 1, user_dict['mention']]
    if chat.type =='private':
        await CHANNEL.log(
            f"#PRIVATE\n{user_dict['mention']} send you\n\n"
            f"{message.text}")
    else:
        await CHANNEL.log(
            "#GROUP\n"
            f"{user_dict['mention']} tagged you in [{chat.title}](http://t.me/{chat.username})\n\n"
            f"{message.text}\n\n[goto_msg](https://t.me/c/{str(chat.id)[4:]}/{message.message_id})")
    AFK_COLLECTION.update_one({'_id': user_id},
                              {"$set": {
                                  'pcount': USERS[user_id][0],
                                  'gcount': USERS[user_id][1],
                                  'men': USERS[user_id][2]}},
                              upsert=True)


@userge.on_filters(IS_AFK_FILTER & Filters.outgoing, group=-1)
async def handle_afk_outgoing(message: Message):
    global IS_AFK
    IS_AFK = False
    afk_time = time_formatter(round(time.time() - TIME))
    replied: Message = await message.reply(f"`I'm no longer AFK!`", log=__name__)
    if USERS:
        p_msg = ''
        g_msg = ''
        p_count = 0
        g_count = 0
        for pcount, gcount, men in USERS.values():
            if pcount:
                p_msg += f"👤 {men} ✉️ **{pcount}**\n"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**\n"
                g_count += gcount
        await replied.edit(
            f"`You recieved {p_count + g_count} messages while you were away. "
            f"Check log for more details.`\n\n**AFK time** : __{afk_time}__", del_in=3)
        out_str = f"You've recieved **{p_count + g_count}** messages " + \
            f"from **{len(USERS)}** users while you were away!\n\n**AFK time** : __{afk_time}__\n"
        if p_count:
            out_str += f"\n**{p_count} Private Messages:**\n\n{p_msg}"
        if g_count:
            out_str += f"\n**{g_count} Group Messages:**\n\n{g_msg}"
        await CHANNEL.log(out_str)
        USERS.clear()
    else:
        await asyncio.sleep(3)
        await replied.delete()
    AFK_COLLECTION.drop()
    SAVED_SETTINGS.update_one(
        {'_id': 'AFK'}, {"$set": {'on': False}}, upsert=True)


AFK_REASONS = (
    "I'm busy right now. Please talk in a bag and when I come back you can just give me the bag!",
    "I'm away right now. If you need anything, leave a message after the beep: \
`beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep!`",
    "You missed me, next time aim better.",
    "I'll be back in a few minutes and if I'm not...,\nwait longer.",
    "I'm not here right now, so I'm probably somewhere else.",
    "Roses are red,\nViolets are blue,\nLeave me a message,\nAnd I'll get back to you.",
    "Sometimes the best things in life are worth waiting for…\nI'll be right back.",
    "I'll be right back,\nbut if I'm not right back,\nI'll be back later.",
    "If you haven't figured it out already,\nI'm not here.",
    "I'm away over 7 seas and 7 countries,\n7 waters and 7 continents,\n7 mountains and 7 hills,\
7 plains and 7 mounds,\n7 pools and 7 lakes,\n7 springs and 7 meadows,\
7 cities and 7 neighborhoods,\n7 blocks and 7 houses...\
    Where not even your messages can reach me!",
    "I'm away from the keyboard at the moment, but if you'll scream loud enough at your screen,\
    I might just hear you.",
    "I went that way\n>>>>>",
    "I went this way\n<<<<<",
    "Please leave a message and make me feel even more important than I already am.",
    "If I were here,\nI'd tell you where I am.\n\nBut I'm not,\nso ask me when I return...",
    "I am away!\nI don't know when I'll be back!\nHopefully a few minutes from now!",
    "I'm not available right now so please leave your name, number, \
    and address and I will stalk you later. :P",
    "Sorry, I'm not here right now.\nFeel free to talk to my userbot as long as you like.\
I'll get back to you later.",
    "I bet you were expecting an away message!",
    "Life is so short, there are so many things to do...\nI'm away doing one of them..",
    "I am not here right now...\nbut if I was...\n\nwouldn't that be awesome?")
