"""
eXuCoDeR Music Bot - Admin Checker
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import time
from functools import wraps
from pyrogram import enums, types
from anony import app, db

_admin_cache = {}
_admin_cache_time = {}


async def reload_admins(chat_id: int, wait: bool = False):
    """Reload admin list for a chat with rate limiting."""
    now = time.time()
    last_reload = _admin_cache_time.get(chat_id, 0)

    if wait and (now - last_reload) < 600:
        return False

    try:
        admins = []
        async for member in app.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            admins.append(member.user.id)
        _admin_cache[chat_id] = admins
        _admin_cache_time[chat_id] = now
        await db.set_admins(chat_id, admins)
        return True
    except Exception:
        return False


async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if a user is admin in a chat (with caching)."""
    # Owner and sudoers always pass
    if user_id == app.owner or user_id in app.sudoers:
        return True

    # Check cache
    if chat_id in _admin_cache:
        if user_id in _admin_cache[chat_id]:
            return True

    # Reload if needed
    now = time.time()
    if (now - _admin_cache_time.get(chat_id, 0)) > 600:
        await reload_admins(chat_id)

    return user_id in _admin_cache.get(chat_id, [])


async def can_manage_vc(chat_id: int, user_id: int) -> bool:
    """Check if user can manage voice chat."""
    if user_id == app.owner or user_id in app.sudoers:
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return (
            member.status == enums.ChatMemberStatus.OWNER
            or member.privileges
            and member.privileges.can_manage_video_chats
        )
    except Exception:
        return False


def admin_check(func):
    """Decorator to check admin permissions."""
    @wraps(func)
    async def wrapper(_, message: types.Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        # Owner and sudoers bypass checks
        if user_id == app.owner or user_id in app.sudoers:
            return await func(_, message)

        # Check admin status
        if not await can_manage_vc(chat_id, user_id):
            return await message.reply_text(
                message.lang.get(
                    "user_no_perms",
                    "You don't have permission to manage voice chats."
                )
            )

        return await func(_, message)
    return wrapper
