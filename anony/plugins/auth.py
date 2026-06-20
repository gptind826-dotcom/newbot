"""
eXuCoDeR Music Bot - Auth Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import admin_check, utils


@app.on_message(
    filters.command(["auth"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def auth(_, m: types.Message):
    """Authorize a user to control playback."""
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            m.lang.get("user_not_found", "Reply to a user or provide ID.")
        )

    await db.add_auth(m.chat.id, user.id)
    await m.reply_text(
        m.lang.get("auth_added", "Authorized {0}").format(user.mention)
    )


@app.on_message(
    filters.command(["unauth"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def unauth(_, m: types.Message):
    """Remove user authorization."""
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            m.lang.get("user_not_found", "Reply to a user or provide ID.")
        )

    await db.remove_auth(m.chat.id, user.id)
    await m.reply_text(
        m.lang.get("auth_removed", "Un-authorized {0}").format(user.mention)
    )
