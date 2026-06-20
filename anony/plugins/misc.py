"""
eXuCoDeR Music Bot - Misc Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
from pyrogram import filters, types

from anony import app, lang


@app.on_message(filters.command(["logs"]) & filters.user(app.owner))
@lang.language()
async def logs(_, m: types.Message):
    """Send log file (owner only)."""
    if not os.path.exists("log.txt"):
        return await m.reply_text(
            m.lang.get("log_not_found", "Log file not found.")
        )

    await m.reply_document(
        document="log.txt",
        caption=m.lang.get("log_sent", "Log file").format(
            app.name
        ),
    )


@app.on_message(filters.command(["id"]) & ~app.bl_users)
async def get_id(_, m: types.Message):
    """Get chat/user ID."""
    if m.reply_to_message:
        user = m.reply_to_message.from_user
        if user:
            text = (
                f"<b>User ID:</b> <code>{user.id}</code>\n"
                f"<b>Name:</b> {user.mention}"
            )
        else:
            text = f"<b>Chat ID:</b> <code>{m.chat.id}</code>"
    else:
        text = (
            f"<b>Chat ID:</b> <code>{m.chat.id}</code>\n"
            f"<b>Your ID:</b> <code>{m.from_user.id if m.from_user else 'N/A'}</code>"
        )
    await m.reply_text(text)
