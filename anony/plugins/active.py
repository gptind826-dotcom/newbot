"""
eXuCoDeR Music Bot - Active Calls Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang


@app.on_message(filters.command(["active", "ac"]) & ~app.bl_users)
@lang.language()
async def active(_, m: types.Message):
    """Show active voice calls."""
    sent = await m.reply_text(
        m.lang.get("vc_fetching", "Fetching active calls...")
    )

    calls = await db.get_active_calls()
    count = len(calls)

    if not calls:
        return await sent.edit_text(
            m.lang.get("vc_empty", "No active streams.")
        )

    text = (
        f"{m.lang.get('vc_count', 'Active: {0}').format(count)}\n\n"
        f"{m.lang.get('vc_list', 'Active Streams:')}\n"
    )
    for i, cid in enumerate(calls[:20], 1):
        text += f"<code>{i}.</code> <code>{cid}</code>\n"

    await sent.edit_text(text)
