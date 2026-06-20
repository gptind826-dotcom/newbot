"""
eXuCoDeR Music Bot - Broadcast Plugin (Sudo Only)
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang


@app.on_message(
    filters.command(["broadcast", "gcast"]) & filters.user(app.owner)
)
@lang.language()
async def broadcast(_, m: types.Message):
    """Broadcast message to all chats (owner only)."""
    if not m.reply_to_message:
        return await m.reply_text(
            m.lang.get("gcast_usage", "Reply to a message to broadcast.")
        )

    sent = await m.reply_text(
        m.lang.get("gcast_start", "Broadcasting...")
    )

    # Get all chats
    chats = await db.get_active_calls()
    sent_count = 0
    fail_count = 0

    for chat_id in chats:
        try:
            await m.reply_to_message.copy(chat_id)
            sent_count += 1
        except Exception:
            fail_count += 1

    await sent.edit_text(
        m.lang.get("gcast_end",
                  "Broadcast complete:\n"
                  "Sent: {0}\nFailed: {1}").format(sent_count, fail_count)
    )
