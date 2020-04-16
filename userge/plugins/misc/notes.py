# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, get_collection

NOTES_COLLECTION = get_collection("notes")


@userge.on_cmd("notes", about="__List all saved notes__")
async def notes_active(message: Message):
    out = "`There are no saved notes in this chat`"

    for note in NOTES_COLLECTION.find({'chat_id': message.chat.id}, {'name': 1}):
        if out == "`There are no saved notes in this chat`":
            out = "**--Notes saved in this chat:--**\n\n"
            out += " 🔹 `{}`\n".format(note['name'])

        else:
            out += " 🔹 `{}`\n".format(note['name'])

    await message.edit(out)


@userge.on_cmd("delnote", about="""\
__Deletes a note by name__

**Usage:**

    `.delnote [note name]`""")
async def remove_notes(message: Message):
    notename = message.input_str

    if not notename:
        out = "`Wrong syntax`\nNo arguements"

    elif NOTES_COLLECTION.find_one_and_delete({'chat_id': message.chat.id, 'name': notename}):
        out = "`Successfully deleted note:` **{}**".format(notename)

    else:
        out = "`Couldn't find note:` **{}**".format(notename)

    await message.edit(text=out, del_in=3)


@userge.on_cmd(r"(\w[\w_]*)",
               about="""\
__Gets a note by name__

**Usage:**

    `#[notename]`""",
               name="note",
               trigger='#',
               only_me=False)
async def note(message: Message):
    notename = message.matches[0].group(1)
    found = NOTES_COLLECTION.find_one(
        {'chat_id': message.chat.id, 'name': notename}, {'content': 1})

    if found:
        out = "**--{}--**\n\n{}".format(notename, found['content'])

        await message.force_edit(text=out)


@userge.on_cmd("addnote (\\w[\\w_]*)(?:\\s([\\s\\S]+))?",
               about="""\
__Adds a note by name__

**Usage:**

    `.addnote [note name] [content | reply to msg]`""")
async def add_filter(message: Message):
    notename = message.matches[0].group(1)
    content = message.matches[0].group(2)

    if message.reply_to_message:
        content = message.reply_to_message.text

    if not content:
        await message.err(text="No Content Found!")
        return

    out = "`{} note #{}`"
    result = NOTES_COLLECTION.update_one({'chat_id': message.chat.id, 'name': notename},
                                         {"$set": {'content': content}},
                                         upsert=True)

    if result.upserted_id:
        out = out.format('Added', notename)

    else:
        out = out.format('Updated', notename)

    await message.edit(text=out, del_in=3, log=True)
