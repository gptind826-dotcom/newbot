"""
eXuCoDeR Music Bot - Skip Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import anon, app, db, lang
from anony.helpers import admin_check


@app.on_message(
    filters.command(["skip"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def skip(_, m: types.Message):
    """Skip the current track."""
    chat_id = m.chat.id

    if not await db.get_call(chat_id):
        return await m.reply_text(
            m.lang.get("not_playing", "Nothing is playing.")
        )

    await m.reply_text(
        m.lang.get("play_skipped", "Skipped by {0}").format(
            m.from_user.mention if m.from_user else "Anonymous"
        )
    )
    await anon.play_next(chat_id)
