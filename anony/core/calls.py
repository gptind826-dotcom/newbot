"""
eXuCoDeR Music Bot - Voice Call Manager
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import asyncio

from ntgcalls import (ConnectionNotFound, TelegramServerError,
                      RTMPStreamingUnsupported, ConnectionError)
from pyrogram.errors import (ChatSendMediaForbidden, ChatSendPhotosForbidden,
                             MessageIdInvalid)
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types

from anony import (app, config, db, lang, logger,
                   queue, thumb, userbot, yt)
from anony.helpers import Media, Track, buttons


class TgCall:
    """Manages Telegram voice calls and media playback."""

    def __init__(self):
        self.clients = []

    async def pause(self, chat_id: int) -> bool:
        """Pause playback in a chat."""
        client = await db.get_assistant(chat_id)
        if not client:
            return False
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        """Resume playback in a chat."""
        client = await db.get_assistant(chat_id)
        if not client:
            return False
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        """Stop playback and clean up queue in a chat."""
        client = await db.get_assistant(chat_id)

        # Delete current track file before clearing
        current = queue.get_current(chat_id)
        if current and current.file_path:
            await yt.delete_file(current.file_path)

        queue.clear(chat_id)
        await db.remove_call(chat_id)
        await db.set_loop(chat_id, 0)

        if client:
            try:
                await client.leave_call(chat_id)
            except Exception:
                pass

    async def _auto_delete(self, media: Media | Track) -> None:
        """Automatically delete downloaded file after playback."""
        if config.AUTO_DELETE and media and media.file_path:
            await yt.delete_file(media.file_path)

    async def play_media(
        self,
        chat_id: int,
        message: Message,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        """Play media in a voice chat."""
        client = await db.get_assistant(chat_id)
        if not client:
            await message.edit_text(
                "No assistant available. Please try again later."
            )
            return

        _lang = await lang.get_lang(chat_id)

        # Generate thumbnail
        _thumb = None
        if config.THUMB_GEN and isinstance(media, Track):
            try:
                _thumb = await thumb.generate(media)
            except Exception:
                _thumb = config.DEFAULT_THUMB
        elif not config.THUMB_GEN:
            _thumb = config.DEFAULT_THUMB

        # Check file exists
        if not media.file_path or not os.path.exists(media.file_path):
            await message.edit_text(
                _lang.get("error_no_file", "File not found.").format(
                    config.SUPPORT_CHAT
                )
            )
            await self._auto_delete(media)
            return await self.play_next(chat_id)

        # Create media stream
        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if media.video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=f"-ss {seek_time}" if seek_time > 1 else None,
        )

        try:
            await client.play(
                chat_id=chat_id,
                stream=stream,
                config=types.GroupCallConfig(auto_start=False),
            )

            if not seek_time:
                media.time = 1
                await db.add_call(chat_id)

                # Format play message with professional UI
                text = _lang.get("play_media", (
                    "<b>Now Playing</b>\n\n"
                    "<b>Title:</b> <a href='{0}'>{1}</a>\n"
                    "<b>Duration:</b> {2}\n"
                    "<b>Requested by:</b> {3}"
                )).format(
                    media.url or "#",
                    media.title or "Unknown",
                    media.duration or "00:00",
                    media.user or "Anonymous",
                )

                keyboard = buttons.controls(chat_id)

                try:
                    if _thumb:
                        await message.edit_media(
                            media=InputMediaPhoto(
                                media=_thumb,
                                caption=text,
                            ),
                            reply_markup=keyboard,
                        )
                    else:
                        await message.edit_text(text, reply_markup=keyboard)
                except (ChatSendMediaForbidden,
                        ChatSendPhotosForbidden,
                        MessageIdInvalid):
                    if _thumb:
                        sent = await app.send_photo(
                            chat_id=chat_id,
                            photo=_thumb,
                            caption=text,
                            reply_markup=keyboard,
                        )
                    else:
                        sent = await app.send_message(
                            chat_id=chat_id,
                            text=text,
                            reply_markup=keyboard,
                        )
                    media.message_id = sent.id

        except FileNotFoundError:
            await message.edit_text(
                _lang.get("error_no_file", "File not found.").format(
                    config.SUPPORT_CHAT
                )
            )
            await self._auto_delete(media)
            await self.play_next(chat_id)
        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_no_call",
                          "No active voice chat found. Start one and try again.")
            )
        except exceptions.NoAudioSourceFound:
            await message.edit_text(
                _lang.get("error_no_audio",
                          "No audio source found. Skipping...")
            )
            await self._auto_delete(media)
            await self.play_next(chat_id)
        except (ConnectionError, ConnectionNotFound, TelegramServerError):
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_tg_server",
                          "Telegram server error. Please try again.")
            )
        except RTMPStreamingUnsupported:
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_rtmp",
                          "RTMP streaming is not supported.")
            )
        except Exception as e:
            logger.error(f"Play error: {e}")
            await message.edit_text(
                f"An error occurred during playback.\n"
                f"Report: {config.SUPPORT_CHAT}"
            )
            await self._auto_delete(media)
            await self.play_next(chat_id)

    async def replay(self, chat_id: int) -> None:
        """Replay the current track."""
        if not await db.get_call(chat_id):
            return

        media = queue.get_current(chat_id)
        if not media:
            return

        _lang = await lang.get_lang(chat_id)
        msg = await app.send_message(
            chat_id=chat_id,
            text=_lang.get("play_again", "Replaying...")
        )
        media.message_id = msg.id
        await self.play_media(chat_id, msg, media)

    async def play_next(self, chat_id: int) -> None:
        """Play the next track in queue."""
        # Check for loop
        loop = await db.get_loop(chat_id)
        if loop:
            await db.set_loop(chat_id, loop - 1)
            return await self.replay(chat_id)

        # Get current track and auto-delete its file
        current = queue.get_current(chat_id)
        if current:
            try:
                if current.message_id:
                    await app.delete_messages(
                        chat_id=chat_id,
                        message_ids=current.message_id,
                        revoke=True,
                    )
            except Exception:
                pass
            # Auto-delete the file after playing
            await self._auto_delete(current)

        # Get next track
        media = queue.get_next(chat_id)
        if not media:
            return await self.stop(chat_id)

        _lang = await lang.get_lang(chat_id)
        msg = await app.send_message(
            chat_id=chat_id,
            text=_lang.get("play_next",
                          "Loading next track...")
        )

        # Download if needed
        if not media.file_path:
            file_id = getattr(media, 'id', '')
            if file_id:
                await msg.edit_text(
                    _lang.get("play_downloading", "Downloading...")
                )
                media.file_path = await yt.download(file_id, video=media.video)

        if not media.file_path:
            await msg.edit_text(
                _lang.get("error_no_file", "Download failed.").format(
                    config.SUPPORT_CHAT
                )
            )
            await self.play_next(chat_id)
            return

        media.message_id = msg.id
        await self.play_media(chat_id, msg, media)

    async def ping(self) -> float:
        """Get average ping across all clients."""
        if not self.clients:
            return 0.0
        pings = [client.ping for client in self.clients if client.ping]
        if not pings:
            return 0.0
        return round(sum(pings) / len(pings), 2)

    async def decorators(self, client: PyTgCalls) -> None:
        """Set up event handlers for a client."""
        @client.on_update()
        async def update_handler(_, update: types.Update) -> None:
            if isinstance(update, types.StreamEnded):
                if update.stream_type == types.StreamEnded.Type.AUDIO:
                    await self.play_next(update.chat_id)
            elif isinstance(update, types.ChatUpdate):
                if update.status in [
                    types.ChatUpdate.Status.KICKED,
                    types.ChatUpdate.Status.LEFT_GROUP,
                    types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                ]:
                    await self.stop(update.chat_id)

    async def boot(self) -> None:
        """Start all PyTgCalls clients."""
        try:
            # Try to suppress notice display
            from pytgcalls.pytgcalls_session import PyTgCallsSession
            PyTgCallsSession.notice_displayed = True
        except (ImportError, AttributeError):
            pass

        for ub in userbot.clients:
            try:
                client = PyTgCalls(ub, cache_duration=100)
                await client.start()
                self.clients.append(client)
                await self.decorators(client)
            except Exception as e:
                logger.error(f"Failed to start PyTgCalls client: {e}")

        logger.info(f"PyTgCalls: {len(self.clients)} client(s) started.")
