"""
eXuCoDeR Music Bot - Callback Query Handler
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import types

from anony import anon, app, config, db, lang
from anony.helpers import buttons


@app.on_callback_query()
@lang.language()
async def callbacks(_, cb: types.CallbackQuery):
    """Handle all inline button callbacks."""
    data = cb.data.split()
    if not data:
        return await cb.answer("Invalid callback", show_alert=True)

    action = data[0]

    # Help menu callbacks
    if action == "help":
        await _handle_help(cb, data)
    # Control callbacks
    elif action == "controls":
        await _handle_controls(cb, data)
    # Language callbacks
    elif action == "language":
        await _handle_language(cb)
    elif action == "lang_change":
        await _handle_lang_change(cb, data)
    # Settings callbacks
    elif action == "settings":
        await _handle_settings(cb, data)
    else:
        await cb.answer("Unknown action", show_alert=True)


async def _handle_help(cb: types.CallbackQuery, data: list):
    """Handle help menu navigation."""
    sub_action = data[1] if len(data) > 1 else None

    if sub_action == "back":
        await cb.edit_message_text(
            text=cb.lang.get("help_menu",
                           "Click the buttons below for command info."),
            reply_markup=buttons.help_markup(cb.lang),
        )
    elif sub_action == "close":
        await cb.message.delete()
    elif sub_action:
        # Show specific help section
        help_key = f"help_{sub_action}"
        help_text = cb.lang.get(help_key, f"Help for {sub_action}")
        await cb.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(cb.lang, back=True),
        )
    else:
        await cb.answer()


async def _handle_controls(cb: types.CallbackQuery, data: list):
    """Handle player control buttons."""
    if len(data) < 3:
        return await cb.answer("Invalid control", show_alert=True)

    control = data[1]
    chat_id = int(data[2])

    # Check permissions
    if cb.from_user.id not in app.sudoers:
        adminlist = await db.get_admins(chat_id)
        if cb.from_user.id not in adminlist:
            return await cb.answer(
                "You don't have permission!", show_alert=True
            )

    if control == "pause":
        await anon.pause(chat_id)
        await cb.answer("Paused")
    elif control == "resume":
        await anon.resume(chat_id)
        await cb.answer("Resumed")
    elif control == "skip":
        await anon.play_next(chat_id)
        await cb.answer("Skipped")
    elif control == "stop":
        await anon.stop(chat_id)
        await cb.answer("Stopped")
    elif control == "replay":
        await anon.replay(chat_id)
        await cb.answer("Replaying")
    elif control == "force" and len(data) >= 4:
        item_id = data[3]
        # Force play logic
        await cb.answer("Playing now...")
    else:
        await cb.answer()


async def _handle_language(cb: types.CallbackQuery):
    """Show language selection."""
    current_lang = await db.get_lang(cb.message.chat.id)
    await cb.edit_message_text(
        text=cb.lang.get("lang_choose", "Choose a language:"),
        reply_markup=buttons.lang_markup(current_lang),
    )


async def _handle_lang_change(cb: types.CallbackQuery, data: list):
    """Change language."""
    if len(data) < 2:
        return await cb.answer("Invalid language", show_alert=True)

    lang_code = data[1]
    chat_id = cb.message.chat.id

    await db.set_lang(chat_id, lang_code)
    await cb.answer(f"Language changed to {lang_code}")

    # Refresh message
    await cb.edit_message_text(
        text=cb.lang.get("lang_changed",
                        "Language changed to {0}").format(lang_code),
    )


async def _handle_settings(cb: types.CallbackQuery, data: list):
    """Handle settings toggles."""
    if len(data) < 2:
        return await cb.answer()

    setting = data[1]
    chat_id = cb.message.chat.id

    if setting == "play":
        await db.toggle_play_mode(chat_id)
        current = await db.get_play_mode(chat_id)
        await cb.answer(f"Admin-only play: {current}")
    elif setting == "delete":
        await db.toggle_cmd_delete(chat_id)
        current = await db.get_cmd_delete(chat_id)
        await cb.answer(f"Command delete: {current}")

    # Refresh settings
    admin_only = await db.get_play_mode(chat_id)
    cmd_delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    await cb.edit_message_text(
        text=cb.lang.get("start_settings",
                        "Settings for this chat.").format(
            cb.message.chat.title
        ),
        reply_markup=buttons.settings_markup(
            cb.lang, admin_only, cmd_delete, _language, chat_id
        ),
    )
