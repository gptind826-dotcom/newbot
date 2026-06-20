"""
eXuCoDeR Music Bot - YouTube Integration
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import re
import asyncio
import aiohttp
from pathlib import Path

from anony import config, logger
from anony.helpers import Track
from anony.helpers._utilities import utils


class YouTube:
    """YouTube video/audio download and search functionality."""

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )

    def get_cookies(self):
        """Get a random cookie file for downloads."""
        if not self.checked:
            try:
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            except FileNotFoundError:
                pass
            self.checked = True

        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("No cookies found; downloads may fail.")
            return None
        return self.cookies[0] if self.cookies else None

    async def save_cookies(self, urls: list[str]) -> None:
        """Download and save cookies from URLs."""
        logger.info("Downloading cookies...")
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split("/")[-1]
                link = "https://batbin.me/raw/" + name
                try:
                    async with session.get(link) as resp:
                        resp.raise_for_status()
                        cookie_path = f"{self.cookie_dir}/{name}.txt"
                        with open(cookie_path, "wb") as fw:
                            fw.write(await resp.read())
                        self.cookies.append(cookie_path)
                except Exception as e:
                    logger.warning(f"Failed to download cookie from {url}: {e}")
        logger.info(f"Cookies saved: {len(self.cookies)} files")

    def valid(self, url: str) -> bool:
        """Check if URL is a valid YouTube link."""
        return bool(self.regex.match(url))

    def invalid(self, url: str) -> bool:
        """Check if URL looks like YouTube but is invalid format."""
        return bool(self.iregex.match(url))

    async def search(
        self, query: str, m_id: int, video: bool = False
    ) -> Track | None:
        """Search YouTube for a video."""
        try:
            from py_yt import VideosSearch
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception:
            return None

        if results and results.get("result"):
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title", "Unknown")[:50],
                thumbnail=data.get("thumbnails", [{}])[-1]
                .get("url", "").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short", ""),
                video=video,
            )
        return None

    async def playlist(
        self, limit: int, user: str, url: str, video: bool
    ) -> list[Track | None]:
        """Fetch videos from a YouTube playlist."""
        tracks = []
        try:
            from py_yt import Playlist
            plist = await Playlist.get(url)
            for data in plist.get("videos", [])[:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title", "Unknown")[:50],
                    thumbnail=data.get("thumbnails", [{}])[-1]
                    .get("url", "").split("?")[0],
                    url=data.get("link", "").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.warning(f"Playlist fetch failed: {e}")
        return tracks

    async def download(
        self, video_id: str, video: bool = False
    ) -> str | None:
        """Download a YouTube video/audio."""
        import yt_dlp

        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        # Return cached file if exists
        if Path(filename).exists():
            return filename

        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "cookiefile": cookie,
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": (
                    "(bestvideo[height<=?720][width<=?1280][ext=mp4])+"
                    "(bestaudio)"
                ),
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except (yt_dlp.utils.DownloadError,
                        yt_dlp.utils.ExtractorError):
                    return None
                except Exception as ex:
                    logger.warning(f"Download failed: {ex}")
                    return None
            return filename

        return await asyncio.to_thread(_download)

    async def delete_file(self, file_path: str) -> None:
        """Delete a downloaded file after playback."""
        if not file_path:
            return
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Auto-deleted: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete {file_path}: {e}")
