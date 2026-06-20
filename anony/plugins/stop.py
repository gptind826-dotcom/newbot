"""
eXuCoDeR Music Bot - Stop Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import anon, app, db, lang
from anony.helpers import admin_check


@app.on_message(
    filters.command(["stop"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def stop(_, m: types.Message):
    """Stop playback and clear queue."""
    chat_id = m.chat.id

    if not await db.get_call(chat_id):
        return await m.reply_text(
            m.lang.get("not_playing", "Nothing is playing.")
        )

    await anon.stop(chat_id)
    await m.reply_text(
        m.lang.get("play_stopped", "Stopped by {0}").format(
            m.from_user.mention if m.from_user else "Anonymous"
        )
    )
