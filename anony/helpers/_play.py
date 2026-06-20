"""
eXuCoDeR Music Bot - Play Handler Decorator
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import asyncio

from pyrogram import enums, errors, types

from anony import app, config, db, logger, queue, yt
from anony.helpers import utils


def checkUB(play):
    """Decorator to validate play preconditions."""
    async def wrapper(_, m: types.Message):
        if not m.from_user:
            return await m.reply_text(
                m.lang.get("play_user_invalid",
                          "Anonymous users cannot use this command.")
            )

        chat_id = m.chat.id
        if m.chat.type != enums.ChatType.SUPERGROUP:
            await m.reply_text(
                m.lang.get("play_chat_invalid",
                          "This bot only works in supergroups.")
            )
            return await app.leave_chat(chat_id)

        # Check for query
        if not m.reply_to_message and (
            len(m.command) < 2
            or (len(m.command) == 2 and m.command[1] == "-f")
        ):
            return await m.reply_text(
                m.lang.get("play_usage", "Usage: /play <song name>")
            )

        # Check queue limit
        if len(queue.get_queue(chat_id)) >= config.QUEUE_LIMIT:
            return await m.reply_text(
                m.lang.get("play_queue_full",
                          "Queue is full.").format(config.QUEUE_LIMIT)
            )

        # Parse flags
        force = (
            m.command[0].endswith("force")
            or (len(m.command) > 1 and "-f" in m.command[1:])
        )
        video = (
            m.command[0].startswith("v")
            and config.VIDEO_PLAY
        )
        url = utils.get_url(m)

        if url and yt.invalid(url):
            return await m.reply_text(
                m.lang.get("play_not_found",
                          "Invalid URL.").format(config.SUPPORT_CHAT)
            )
        m3u8 = url and not yt.valid(url)

        # Check play mode (admin only)
        play_mode = await db.get_play_mode(chat_id)
        if play_mode and not force:
            adminlist = await db.get_admins(chat_id)
            if (
                m.from_user.id not in adminlist
                and not await db.is_auth(chat_id, m.from_user.id)
                and m.from_user.id not in app.sudoers
            ):
                return await m.reply_text(
                    m.lang.get("play_admin",
                              "Only admins can play in this chat.")
                )

        # Ensure assistant is in chat
        if chat_id not in db.active_calls:
            client = await db.get_client(chat_id)
            if client:
                try:
                    member = await app.get_chat_member(chat_id, client.id)
                    if member.status in [
                        enums.ChatMemberStatus.BANNED,
                        enums.ChatMemberStatus.RESTRICTED,
                    ]:
                        try:
                            await app.unban_chat_member(
                                chat_id=chat_id, user_id=client.id
                            )
                        except Exception:
                            return await m.reply_text(
                                m.lang.get("play_banned",
                                          "Assistant is banned.").format(
                                    app.name, client.id,
                                    client.mention,
                                    f"@{client.username}" if client.username else "N/A",
                                )
                            )
                except errors.ChatAdminRequired:
                    return await m.reply_text(
                        m.lang.get("admin_required",
                                  "Bot needs admin privileges.")
                    )
                except errors.UserNotParticipant:
                    # Invite assistant
                    try:
                        if m.chat.username:
                            invite_link = m.chat.username
                        else:
                            invite_link = (await app.get_chat(chat_id)).invite_link
                            if not invite_link:
                                invite_link = await app.export_chat_invite_link(
                                    chat_id
                                )
                    except errors.ChatAdminRequired:
                        return await m.reply_text(
                            m.lang.get("admin_required",
                                      "Bot needs admin privileges.")
                        )
                    except Exception as ex:
                        return await m.reply_text(
                            m.lang.get("play_invite_error",
                                      "Failed to invite assistant.").format(
                                type(ex).__name__
                            )
                        )

                    umm = await m.reply_text(
                        m.lang.get("play_invite",
                                  "Inviting assistant...").format(app.name)
                    )
                    await asyncio.sleep(2)
                    try:
                        await client.join_chat(invite_link)
                    except errors.UserAlreadyParticipant:
                        pass
                    except Exception as ex:
                        return await umm.edit_text(
                            m.lang.get("play_invite_error",
                                      "Failed to invite assistant.").format(
                                type(ex).__name__
                            )
                        )
                    await umm.delete()

        # Delete command if enabled
        if await db.get_cmd_delete(chat_id):
            try:
                await m.delete()
            except Exception:
                pass

        return await play(_, m, force, m3u8, video, url)
    return wrapper
