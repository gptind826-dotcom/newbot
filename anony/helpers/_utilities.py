"""
eXuCoDeR Music Bot - Utilities
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import re
import time
from pyrogram import enums, types
from anony import app


class Utilities:
    """General utility functions for the bot."""

    def __init__(self):
        pass

    def format_eta(self, seconds: int) -> str:
        """Format seconds into human-readable ETA."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d} min"
        else:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d} h"

    def format_size(self, bytes_size: int) -> str:
        """Format bytes into human-readable size."""
        if bytes_size >= 1024 ** 3:
            return f"{bytes_size / 1024 ** 3:.2f} GB"
        elif bytes_size >= 1024 ** 2:
            return f"{bytes_size / 1024 ** 2:.2f} MB"
        else:
            return f"{bytes_size / 1024:.2f} KB"

    def to_seconds(self, time_str: str) -> int:
        """Convert duration string (HH:MM:SS) to seconds."""
        if not time_str:
            return 0
        try:
            parts = [int(p) for p in str(time_str).strip().split(":")]
            return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))
        except (ValueError, TypeError):
            return 0

    def get_url(self, message_1: types.Message) -> str | None:
        """Extract URL from a message."""
        if not message_1:
            return None

        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            entities = message.entities or message.caption_entities or []
            for entity in entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    return entity.url.split("&si")[0].split("?si")[0]
                elif entity.type == enums.MessageEntityType.URL:
                    text = message.text or message.caption
                    if text:
                        return text[
                            entity.offset: entity.offset + entity.length
                        ].split("&si")[0].split("?si")[0]
        return None

    async def extract_user(self, msg: types.Message) -> types.User | None:
        """Extract user from a message (reply or mention)."""
        if msg.reply_to_message:
            return msg.reply_to_message.from_user

        if msg.entities:
            for e in msg.entities:
                if e.type == enums.MessageEntityType.TEXT_MENTION:
                    return e.user

        if msg.text:
            try:
                if m := re.search(r"@(\w{5,32})", msg.text):
                    return await app.get_users(m.group(0))
                if m := re.search(r"\b\d{6,15}\b", msg.text):
                    return await app.get_users(int(m.group(0)))
            except Exception:
                pass
        return None

    async def play_log(
        self, m: types.Message, link: str, title: str, duration: str
    ) -> None:
        """Send play log to logger group."""
        if m.chat.id == app.logger:
            return
        try:
            _text = m.lang.get("play_log", (
                "<b>Play Log</b>\n\n"
                "<b>Bot:</b> {0}\n"
                "<b>Chat:</b> <code>{1}</code> | {2}\n"
                "<b>User:</b> <code>{3}</code> | {4}\n"
                "<b>Message:</b> {5}\n\n"
                "<b>Title:</b> {6}\n"
                "<b>Duration:</b> {7}"
            )).format(
                app.name, m.chat.id, m.chat.title,
                m.from_user.id if m.from_user else 0,
                m.from_user.mention if m.from_user else "Anonymous",
                link, title, duration,
            )
            await app.send_message(chat_id=app.logger, text=_text)
        except Exception:
            pass

    async def send_log(
        self, m: types.Message, chat: bool = False
    ) -> None:
        """Send user/chat join log to logger group."""
        try:
            if chat:
                user = m.from_user
                text = m.lang.get("log_chat", (
                    "<b>New Chat</b>\n\n"
                    "<b>Chat:</b> <code>{0}</code> | {1}\n"
                    "<b>User:</b> <code>{2}</code> | {3}"
                )).format(
                    m.chat.id, m.chat.title,
                    user.id if user else 0,
                    user.mention if user else "Anonymous",
                )
            else:
                text = m.lang.get("log_user", (
                    "<b>New User</b>\n\n"
                    "<b>ID:</b> <code>{0}</code>\n"
                    "<b>Name:</b> {1} | {2}"
                )).format(
                    m.from_user.id,
                    f"@{m.from_user.username}" if m.from_user.username else "N/A",
                    m.from_user.mention,
                )
            await app.send_message(chat_id=app.logger, text=text)
        except Exception:
            pass

    @staticmethod
    def uptime(start_time: float) -> str:
        """Calculate uptime from boot timestamp."""
        total_seconds = int(time.time() - start_time)
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)
