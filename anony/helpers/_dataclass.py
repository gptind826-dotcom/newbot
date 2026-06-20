"""
eXuCoDeR Music Bot - Data Classes
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from dataclasses import dataclass, field


@dataclass
class Media:
    """Represents a media item for playback."""
    id: str
    duration: str = "00:00"
    duration_sec: int = 0
    file_path: str = None
    message_id: int = 0
    title: str = "Unknown"
    url: str = None
    time: int = 0
    user: str = "Anonymous"
    video: bool = False


@dataclass
class Track:
    """Represents a YouTube track for playback."""
    id: str
    channel_name: str = None
    duration: str = "00:00"
    duration_sec: int = 0
    title: str = "Unknown"
    url: str = None
    file_path: str = None
    message_id: int = 0
    time: int = 0
    thumbnail: str = None
    user: str = "Anonymous"
    view_count: str = None
    video: bool = False
