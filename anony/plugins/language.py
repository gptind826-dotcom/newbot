"""
eXuCoDeR Music Bot - Language Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import buttons


@app.on_message(
    filters.command(["lang", "language"]) & ~app.bl_users
)
@lang.language()
async def language(_, m: types.Message):
    """Change bot language."""
    current_lang = await db.get_lang(m.chat.id)
    await m.reply_text(
        m.lang.get("lang_choose", "Choose a language:"),
        reply_markup=buttons.lang_markup(current_lang),
    )
