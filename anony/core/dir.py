"""
eXuCoDeR Music Bot - Directory Setup
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os


def ensure_dirs():
    """Create necessary directories for the bot."""
    dirs = [
        "downloads",
        "cache",
        "anony/cookies",
    ]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
