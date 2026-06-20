"""
eXuCoDeR Music Bot - Sudoers Plugin (Owner Only)
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import utils


@app.on_message(
    filters.command(["addsudo"]) & filters.user(app.owner)
)
@lang.language()
async def add_sudo(_, m: types.Message):
    """Add a sudo user (owner only)."""
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            m.lang.get("user_not_found", "Reply to a user or provide ID.")
        )

    sudoers = await db.get_sudoers()
    if user.id in sudoers:
        return await m.reply_text(
            m.lang.get("sudo_already", "{0} is already sudo.").format(
                user.mention
            )
        )

    await db.add_sudoer(user.id)
    app.sudoers.add(user.id)
    await m.reply_text(
        m.lang.get("sudo_added", "Added {0} as sudo.").format(user.mention)
    )


@app.on_message(
    filters.command(["rmsudo"]) & filters.user(app.owner)
)
@lang.language()
async def rm_sudo(_, m: types.Message):
    """Remove a sudo user (owner only)."""
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            m.lang.get("user_not_found", "Reply to a user or provide ID.")
        )

    sudoers = await db.get_sudoers()
    if user.id not in sudoers:
        return await m.reply_text(
            m.lang.get("sudo_not", "{0} is not sudo.").format(user.mention)
        )

    await db.remove_sudoer(user.id)
    app.sudoers.discard(user.id)
    await m.reply_text(
        m.lang.get("sudo_removed", "Removed {0} from sudo.").format(
            user.mention
        )
    )


@app.on_message(
    filters.command(["sudolist"]) & ~app.bl_users
)
@lang.language()
async def sudo_list(_, m: types.Message):
    """List all sudo users."""
    sudoers = await db.get_sudoers()

    text = m.lang.get("sudo_owner", "<b>Owner:</b>\n- {0}\n\n").format(
        (await app.get_users(app.owner)).mention
    )

    if sudoers:
        text += m.lang.get("sudo_users", "<b>Sudo Users:</b>") + "\n"
        for uid in sudoers:
            try:
                user = await app.get_users(uid)
                text += f"- {user.mention}\n"
            except Exception:
                text += f"- <code>{uid}</code>\n"
    else:
        text += "<i>No sudo users.</i>"

    await m.reply_text(text)
