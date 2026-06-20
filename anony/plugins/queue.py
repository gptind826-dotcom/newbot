"""
eXuCoDeR Music Bot - Queue Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang, queue


@app.on_message(
    filters.command(["queue", "q"]) & filters.group & ~app.bl_users
)
@lang.language()
async def show_queue(_, m: types.Message):
    """Display the current queue."""
    chat_id = m.chat.id

    sent = await m.reply_text(
        m.lang.get("queue_fetching", "Fetching queue...")
    )

    q = queue.get_queue(chat_id)
    if not q:
        return await sent.edit_text(
            m.lang.get("vc_empty", "Queue is empty.")
        )

    current = q[0] if q else None
    rest = q[1:] if len(q) > 1 else []

    # Build queue display
    text = ""
    if current:
        text += m.lang.get("queue_curr",
                          "<b>Now Playing:</b>\n"
                          "<b>Title:</b> <a href='{0}'>{1}</a>\n"
                          "<b>Duration:</b> {2}\n"
                          "<b>Requested by:</b> {3}\n\n"
                          ).format(
            current.url or "#",
            current.title or "Unknown",
            current.duration or "00:00",
            current.user or "Anonymous",
        )

    if rest:
        text += "<b>Up Next:</b>\n"
        for i, item in enumerate(rest, 1):
            text += m.lang.get("queue_item",
                              "{0}. {1} - {2}\n"
                              ).format(i, item.title, item.duration)
    else:
        text += "<i>No more tracks in queue.</i>"

    playing = await db.get_call(chat_id)
    await sent.edit_text(
        text,
        reply_markup=queue_markup(
            chat_id,
            m.lang.get("paused" if not playing else "playing", "Status"),
            playing
        ),
    )


def queue_markup(chat_id: int, text: str, playing: bool):
    """Create queue control button."""
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    action = "pause" if playing else "resume"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(text=text,
                            callback_data=f"controls {action} {chat_id} q")
    ]])
