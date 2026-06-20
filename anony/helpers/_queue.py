"""
eXuCoDeR Music Bot - Queue Manager
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from collections import defaultdict, deque
from typing import Union

from ._dataclass import Media, Track

MediaItem = Union[Media, Track]


class Queue:
    """Manages media queues per chat."""

    def __init__(self):
        self.queues: dict[int, deque[MediaItem]] = defaultdict(deque)

    def add(self, chat_id: int, item: MediaItem) -> int:
        """Add an item to the queue. Returns 0 if first (playing), else position."""
        self.queues[chat_id].append(item)
        position = len(self.queues[chat_id]) - 1
        return position

    def check_item(self, chat_id: int, item_id: str) -> tuple[int, MediaItem | None]:
        """Check if item exists in queue by ID."""
        for i, track in enumerate(self.queues[chat_id]):
            if track.id == item_id:
                return i, track
        return -1, None

    def force_add(
        self, chat_id: int, item: MediaItem, remove: int = 0
    ) -> None:
        """Force add item at front of queue (play now)."""
        self.queues[chat_id].appendleft(item)
        if remove:
            try:
                for _ in range(remove):
                    if len(self.queues[chat_id]) > 1:
                        self.queues[chat_id].pop()
            except IndexError:
                pass

    def get_current(self, chat_id: int) -> MediaItem | None:
        """Get currently playing item."""
        if self.queues[chat_id]:
            return self.queues[chat_id][0]
        return None

    def get_next(self, chat_id: int, check: bool = False) -> MediaItem | None:
        """Get next item and remove current."""
        if not self.queues[chat_id]:
            return None
        if check:
            return self.queues[chat_id][1] if len(self.queues[chat_id]) > 1 else None
        self.queues[chat_id].popleft()
        return self.queues[chat_id][0] if self.queues[chat_id] else None

    def get_queue(self, chat_id: int) -> list[MediaItem]:
        """Get full queue list."""
        return list(self.queues[chat_id])

    def remove_current(self, chat_id: int) -> None:
        """Remove currently playing item."""
        if self.queues[chat_id]:
            self.queues[chat_id].popleft()

    def clear(self, chat_id: int) -> None:
        """Clear entire queue."""
        self.queues[chat_id].clear()
