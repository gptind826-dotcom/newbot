"""
eXuCoDeR Music Bot - Blacklist Plugin (Sudo Only)
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang


@app.on_message(
    filters.command(["blacklist", "bl"]) & filters.user(app.sudoers)
)
@lang.language()
async def blacklist_cmd(_, m: types.Message):
    """Blacklist a chat or user (sudo only)."""
    if len(m.command) < 2:
        return await m.reply_text(
            m.lang.get("bl_usage", "Usage: /blacklist <id>")
        )

    try:
        target_id = int(m.command[1])
    except ValueError:
        return await m.reply_text(
            m.lang.get("bl_invalid", "Invalid ID.")
        )

    if target_id in db.blacklisted:
        return await m.reply_text(
            m.lang.get("bl_already", "Already blacklisted.")
        )

    await db.add_blacklist(target_id)
    await m.reply_text(
        m.lang.get("bl_added", "Blacklisted: {0}").format(target_id)
    )


@app.on_message(
    filters.command(["unblacklist", "unbl"]) & filters.user(app.sudoers)
)
@lang.language()
async def unblacklist_cmd(_, m: types.Message):
    """Remove a chat or user from blacklist (sudo only)."""
    if len(m.command) < 2:
        return await m.reply_text(
            m.lang.get("bl_usage", "Usage: /unblacklist <id>")
        )

    try:
        target_id = int(m.command[1])
    except ValueError:
        return await m.reply_text(
            m.lang.get("bl_invalid", "Invalid ID.")
        )

    if target_id not in db.blacklisted:
        return await m.reply_text(
            m.lang.get("bl_not", "Not blacklisted.")
        )

    await db.remove_blacklist(target_id)
    await m.reply_text(
        m.lang.get("bl_removed", "Un-blacklisted: {0}").format(target_id)
    )
