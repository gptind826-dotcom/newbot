"""
eXuCoDeR Music Bot - Restart Plugin (Owner Only)
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import sys
from pyrogram import filters, types

from anony import app, lang


@app.on_message(
    filters.command(["restart"]) & filters.user(app.owner)
)
@lang.language()
async def restart(_, m: types.Message):
    """Restart the bot (owner only)."""
    await m.reply_text(
        m.lang.get("restarting", "Restarting bot...")
    )
    os.execv(sys.executable, [sys.executable, "app.py"])
