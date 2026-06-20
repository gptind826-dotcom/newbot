"""
eXuCoDeR Music Bot - Telegram Utilities
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import aiohttp
import asyncio

from pyrogram import types

from anony import app, config, logger
from anony.helpers import Media


class Telegram:
    """Telegram utility functions for media handling."""

    def __init__(self):
        self.active_downloads = {}
        self.session = None

    async def start(self):
        """Initialize aiohttp session."""
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    def get_media(self, message: types.Message) -> Media | None:
        """Extract media info from a message."""
        if not message:
            return None

        media_types = ["audio", "video", "voice", "video_note", "document"]
        for media_type in media_types:
            media = getattr(message, media_type, None)
            if media:
                is_video = media_type in ["video", "video_note"]
                return Media(
                    id=str(media.file_id),
                    title=media.file_name or "Telegram Media",
                    duration=getattr(media, "duration", "00:00"),
                    duration_sec=getattr(media, "duration", 0),
                    url=message.link if hasattr(message, "link") else None,
                    video=is_video,
                )
        return None

    async def download(
        self, message: types.Message, status_message: types.Message
    ) -> Media | None:
        """Download media from a Telegram message."""
        media = self.get_media(message)
        if not media:
            return None

        download_id = status_message.id
        self.active_downloads[download_id] = True

        try:
            file_path = await message.download(
                file_name=f"downloads/{media.id}"
            )
            media.file_path = file_path
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
        finally:
            self.active_downloads.pop(download_id, None)

        return media

    async def process_m3u8(
        self, url: str, message_id: int, video: bool = False
    ) -> Media:
        """Process M3U8 stream URL."""
        return Media(
            id=f"m3u8_{message_id}",
            title="M3U8 Stream",
            url=url,
            file_path=url,
            video=video,
        )

    async def download_url(
        self, url: str, file_name: str, status_message: types.Message = None
    ) -> str | None:
        """Download a file from URL."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                file_path = f"downloads/{file_name}"
                with open(file_path, "wb") as f:
                    f.write(await resp.read())
                return file_path
        except Exception as e:
            logger.error(f"URL download failed: {e}")
            return None
