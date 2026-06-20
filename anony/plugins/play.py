"""
eXuCoDeR Music Bot - Play Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pathlib import Path

from pyrogram import filters, types

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import buttons, utils
from anony.helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    """Add playlist tracks to queue and return formatted list."""
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text


@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    """Handle play commands with professional UX."""
    sent = await m.reply_text(
        m.lang.get("play_searching", "Searching...")
    )
    file = None
    mention = m.from_user.mention if m.from_user else "Anonymous"
    tracks = []

    # Handle reply-to media
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    # Handle M3U8 stream
    elif m3u8:
        file = await tg.process_m3u8(url, sent.id, video)

    # Handle URL
    elif url:
        if "playlist" in url:
            await sent.edit_text(
                m.lang.get("playlist_fetch", "Fetching playlist...")
            )
            tracks = await yt.playlist(
                config.PLAYLIST_LIMIT, mention, url, video
            )
            if not tracks:
                return await sent.edit_text(
                    m.lang.get("playlist_error",
                              "Failed to fetch playlist.")
                )
            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id, video=video)

        if not file:
            return await sent.edit_text(
                m.lang.get("play_not_found",
                          "Not found.").format(config.SUPPORT_CHAT)
            )

    # Handle search query
    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        # Remove flags from query
        query = query.replace("-f", "").replace("-v", "").strip()
        file = await yt.search(query, sent.id, video=video)
        if not file:
            return await sent.edit_text(
                m.lang.get("play_not_found",
                          "Not found.").format(config.SUPPORT_CHAT)
            )

    if not file:
        return await sent.edit_text(
            m.lang.get("play_usage", "Usage: /play <song name>")
        )

    # Check duration limit
    if file.duration_sec > config.DURATION_LIMIT:
        return await sent.edit_text(
            m.lang.get("play_duration_limit",
                      "Duration limit exceeded.").format(
                config.DURATION_LIMIT // 60
            )
        )

    # Log play
    if await db.is_logger():
        await utils.play_log(m, sent.link, file.title, file.duration)

    file.user = mention

    if force:
        queue.force_add(m.chat.id, file)
    else:
        position = queue.add(m.chat.id, file)

        # If not first or call already active, show queued
        if position != 0 or await db.get_call(m.chat.id):
            await sent.edit_text(
                m.lang.get("play_queued",
                          "Added to queue.").format(
                    position,
                    file.url or "#",
                    file.title,
                    file.duration,
                    mention,
                ),
                reply_markup=buttons.play_queued(
                    m.chat.id, file.id,
                    m.lang.get("play_now", "Play Now")
                ),
            )
            if tracks:
                added = playlist_to_queue(m.chat.id, tracks)
                await app.send_message(
                    chat_id=m.chat.id,
                    text=m.lang.get("playlist_queued",
                                  "Playlist queued.").format(len(tracks)) + added,
                )
            return

    # Download if needed
    if not file.file_path:
        fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
        if Path(fname).exists():
            file.file_path = fname
        else:
            await sent.edit_text(
                m.lang.get("play_downloading", "Downloading...")
            )
            file.file_path = await yt.download(file.id, video=video)

    # Play
    await anon.play_media(chat_id=m.chat.id, message=sent, media=file)

    # Send playlist info
    if tracks:
        added = playlist_to_queue(m.chat.id, tracks)
        await app.send_message(
            chat_id=m.chat.id,
            text=m.lang.get("playlist_queued",
                          "Playlist queued.").format(len(tracks)) + added,
        )
