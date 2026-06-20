"""
eXuCoDeR Music Bot - Stats Plugin
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import platform
import psutil
import sys
from pyrogram import filters, types

from anony import app, config, db, lang


@app.on_message(filters.command(["stats"]) & ~app.bl_users)
@lang.language()
async def stats(_, m: types.Message):
    """Show bot statistics."""
    sent = await m.reply_text(
        m.lang.get("stats_fetching", "Fetching stats...")
    )

    # System info
    ram = psutil.virtual_memory()
    ram_mb = ram.used // (1024 * 1024)
    ram_gb = ram.total // (1024 * 1024 * 1024)
    cpu_percent = psutil.cpu_percent()
    cpu_cores = psutil.cpu_count()
    disk = psutil.disk_usage("/")
    disk_used = disk.used // (1024 * 1024 * 1024)
    disk_total = disk.total // (1024 * 1024 * 1024)

    # Bot info
    active_calls = len(await db.get_active_calls())
    sudo_count = len(await db.get_sudoers())
    bl_count = len(await db.get_blacklisted())

    # Package versions
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    try:
        import pyrogram
        pr_version = pyrogram.__version__
    except Exception:
        pr_version = "Unknown"
    try:
        import pytgcalls
        ptc_version = pytgcalls.__version__
    except Exception:
        ptc_version = "Unknown"

    text = (
        f"<b>eXuCoDeR Music Bot Statistics</b>\n\n"
        f"<b>Active Streams:</b> <code>{active_calls}</code>\n"
        f"<b>Sudo Users:</b> <code>{sudo_count}</code>\n"
        f"<b>Blacklisted:</b> <code>{bl_count}</code>\n\n"
        f"<b>Platform:</b> <code>{platform.system()} {platform.release()}</code>\n"
        f"<b>Python:</b> <code>v{py_version}</code>\n"
        f"<b>Pyrogram:</b> <code>v{pr_version}</code>\n"
        f"<b>PyTgCalls:</b> <code>v{ptc_version}</code>\n\n"
        f"<b>RAM:</b> <code>{ram_mb}MB / {ram_gb}GB ({ram.percent}%)</code>\n"
        f"<b>CPU:</b> <code>{cpu_percent}% ({cpu_cores} cores)</code>\n"
        f"<b>Disk:</b> <code>{disk_used}GB / {disk_total}GB</code>\n\n"
        f"<i>eXuCoDeR Music Bot v4.0.0</i>"
    )

    await sent.edit_text(text)
