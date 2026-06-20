"""
eXuCoDeR Music Bot - Pause Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import anon, app, db, lang
from anony.helpers import admin_check


@app.on_message(
    filters.command(["pause"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def pause(_, m: types.Message):
    """Pause the current stream."""
    chat_id = m.chat.id

    if not await db.get_call(chat_id):
        return await m.reply_text(
            m.lang.get("not_playing", "Nothing is playing.")
        )

    result = await anon.pause(chat_id)
    if result:
        await m.reply_text(
            m.lang.get("play_paused", "Paused by {0}").format(
                m.from_user.mention if m.from_user else "Anonymous"
            )
        )
    else:
        await m.reply_text(
            m.lang.get("play_already_paused", "Already paused!")
        )
