"""
eXuCoDeR Music Bot - Eval Plugin (Owner Only)
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import filters, types

from anony import app, logger
from anony.helpers import format_exception, meval


@app.on_message(filters.command(["eval", "e"]) & filters.user(app.owner))
async def eval_cmd(_, m: types.Message):
    """Execute Python code (owner only)."""
    if len(m.command) < 2 and not m.reply_to_message:
        return await m.reply_text("Provide code to execute.")

    code = m.reply_to_message.text if m.reply_to_message else " ".join(m.command[1:])

    # Safety: wrap in backticks for display
    result, stdout, stderr = await meval(
        code,
        {
            "app": app,
            "m": m,
            "chat": m.chat,
            "user": m.from_user,
        }
    )

    output = ""
    if stdout:
        output += f"<b>Stdout:</b>\n<code>{stdout[:2000]}</code>\n\n"
    if stderr:
        output += f"<b>Error:</b>\n<code>{format_exception(stderr)}</code>\n\n"
    if result is not None:
        output += f"<b>Result:</b>\n<code>{str(result)[:2000]}</code>"

    if not output:
        output = "<i>No output</i>"

    await m.reply_text(output)
