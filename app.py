#!/usr/bin/env python3
"""
eXuCoDeR Music Bot - Application Entry Point
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.

Usage:
    python app.py
    uv run python app.py
"""

import sys
import subprocess


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "pyrogram", "pytgcalls", "yt_dlp", "pymongo", "Pillow",
        "aiohttp", "motor", "python-dotenv", "py-yt",
    ]
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing required packages...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("Dependencies installed successfully!")


def main():
    """Main entry point."""
    check_dependencies()
    # Launch the bot
    import anony.__main__ as bot
    import asyncio
    try:
        asyncio.get_event_loop().run_until_complete(bot.main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
