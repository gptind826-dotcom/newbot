"""
eXuCoDeR Music Bot - Seek Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import anon, app, db, lang, queue
from anony.helpers import admin_check


@app.on_message(
    filters.command(["seek", "seekback"]) & filters.group & ~app.bl_users
)
@lang.language()
@admin_check
async def seek(_, m: types.Message):
    """Seek to a position in the current track."""
    if len(m.command) < 2:
        return await m.reply_text(
            m.lang.get("play_seek_usage", "Usage: /seek <seconds>")
        )

    try:
        duration = int(m.command[1])
    except ValueError:
        return await m.reply_text(
            m.lang.get("play_seek_usage", "Usage: /seek <seconds>")
        )

    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(
            m.lang.get("not_playing", "Nothing is playing.")
        )

    # Validate duration
    current = queue.get_current(chat_id)
    if current and current.duration_sec:
        if duration >= current.duration_sec:
            return await m.reply_text(
                "Seek time exceeds track duration."
            )

    if duration < 10:
        return await m.reply_text(
            m.lang.get("play_seek_min", "Minimum seek is 10 seconds.")
        )

    # Stop and replay with seek
    is_back = m.command[0] == "seekback"
    seek_time = -duration if is_back else duration

    await m.reply_text(
        m.lang.get("play_seeked",
                  "Seeked to {0}s by {1}").format(
            abs(seek_time),
            m.from_user.mention if m.from_user else "Anonymous"
        )
    )

    # Replay with seek
    client = await db.get_assistant(chat_id)
    if client and current:
        from pytgcalls import types as ptypes
        stream = ptypes.MediaStream(
            media_path=current.file_path,
            audio_parameters=ptypes.AudioQuality.HIGH,
            video_parameters=ptypes.VideoQuality.HD_720p,
            audio_flags=ptypes.MediaStream.Flags.REQUIRED,
            video_flags=(
                ptypes.MediaStream.Flags.AUTO_DETECT
                if current.video
                else ptypes.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=f"-ss {abs(seek_time)}",
        )
        await client.play(chat_id=chat_id, stream=stream)
