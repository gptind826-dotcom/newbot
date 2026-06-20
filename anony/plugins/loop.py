"""
eXuCoDeR Music Bot - Loop Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import admin_check


@app.on_message(
    filters.command(["loop"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def loop_cmd(_, m: types.Message):
    """Set loop count for current track."""
    if len(m.command) < 2:
        # Show current loop status
        current = await db.get_loop(m.chat.id)
        if current:
            return await m.reply_text(
                m.lang.get("loop_count", "Loop: {0}").format(current)
            )
        return await m.reply_text(
            m.lang.get("loop_usage",
                      "Usage: /loop [count|off]")
        )

    arg = m.command[1].lower()
    if arg == "off":
        await db.set_loop(m.chat.id, 0)
        return await m.reply_text(
            m.lang.get("loop_off", "Loop disabled.")
        )

    try:
        count = int(arg)
        if count < 1:
            return await m.reply_text("Loop count must be at least 1.")
        await db.set_loop(m.chat.id, count)
        await m.reply_text(
            m.lang.get("loop_set", "Loop set to {0}").format(count)
        )
    except ValueError:
        await m.reply_text(
            m.lang.get("loop_usage", "Usage: /loop [count|off]")
        )
