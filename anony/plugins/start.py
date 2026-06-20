"""
eXuCoDeR Music Bot - Start Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import asyncio
from pyrogram import enums, filters, types

from anony import app, config, db, lang
from anony.helpers import buttons, utils


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Show help menu in private chat."""
    await m.reply_text(
        text=m.lang.get("help_menu",
                       "Click the buttons below for command info."),
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command with professional welcome."""
    # Check blacklist
    if (
        message.from_user
        and message.from_user.id in app.bl_users
        and message.from_user.id not in db.notified
    ):
        return await message.reply_text(
            message.lang.get("bl_user_notify",
                           "You are blacklisted.")
        )

    # Handle deep link to help
    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE

    # Professional welcome message
    if private:
        _text = (
            f"<b>Welcome {message.from_user.first_name}!</b>\n\n"
            f"I am <b>{app.name}</b> - your professional music streaming "
            f"companion for Telegram voice chats.\n\n"
            f"<b>Features:</b>\n"
            f"High-quality audio/video streaming\n"
            f"YouTube, Spotify, Apple Music support\n"
            f"Smart queue management\n"
            f"Auto-cleanup after playback\n\n"
            f"<i>Click the buttons below to get started!</i>"
        )
    else:
        _text = (
            f"<b>Hey! I'm {app.name}</b>\n\n"
            f"A professional music bot for your group's voice chats.\n"
            f"Add me as admin and use /play to start!"
        )

    key = buttons.start_key(message.lang, private)

    try:
        await message.reply_photo(
            photo=config.START_IMG,
            caption=_text,
            reply_markup=key,
            quote=not private,
        )
    except Exception:
        # Fallback to text if photo fails
        await message.reply_text(
            text=_text,
            reply_markup=key,
            quote=not private,
        )

    # Log new user/chat
    if private:
        if not await db.is_user(message.from_user.id):
            await utils.send_log(message)
            await db.add_user(message.from_user.id)
    else:
        if not await db.is_chat(message.chat.id):
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)


@app.on_message(
    filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users
)
@lang.language()
async def settings(_, message: types.Message):
    """Show settings panel."""
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)

    await message.reply_text(
        text=message.lang.get("start_settings",
                             "<b>{0} Settings</b>\n\n"
                             "Configure bot behavior for this chat.").format(
            message.chat.title
        ),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    """Handle bot being added to a group."""
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
