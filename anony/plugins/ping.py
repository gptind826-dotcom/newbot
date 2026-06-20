"""
eXuCoDeR Music Bot - Ping Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import time
import psutil
from pyrogram import filters, types

from anony import anon, app, boot, lang
from anony.helpers import buttons


@app.on_message(filters.command(["ping"]) & ~app.bl_users)
@lang.language()
async def ping(_, m: types.Message):
    """Show bot status and system info."""
    start = time.time()
    sent = await m.reply_text(
        m.lang.get("pinging", "Pinging...")
    )
    latency = round((time.time() - start) * 1000, 2)

    # System stats
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    uptime_str = _uptime(boot)

    # PyTgCalls ping
    ptc_ping = await anon.ping()

    text = (
        f"<b>eXuCoDeR Music Bot Status</b>\n\n"
        f"<b>Latency:</b> <code>{latency}ms</code>\n"
        f"<b>PyTgCalls:</b> <code>{ptc_ping}ms</code>\n\n"
        f"<b>Uptime:</b> <code>{uptime_str}</code>\n"
        f"<b>CPU:</b> <code>{cpu}%</code>\n"
        f"<b>RAM:</b> <code>{ram}%</code>\n"
        f"<b>Disk:</b> <code>{disk}%</code>\n\n"
        f"<i>System is running smoothly.</i>"
    )

    await sent.edit_text(
        text,
        reply_markup=buttons.ping_markup(
            m.lang.get("support", "Support")
        ),
    )


def _uptime(start_time: float) -> str:
    """Calculate uptime."""
    total = int(time.time() - start_time)
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
