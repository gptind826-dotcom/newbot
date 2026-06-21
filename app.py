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
    # Mapping package names to their actual importable module names
    required_packages = {
        "pyrogram": "pyrogram", 
        "pytgcalls": "pytgcalls", 
        "yt-dlp": "yt_dlp", 
        "pymongo": "pymongo", 
        "Pillow": "PIL",  # Pillow is imported as PIL
        "aiohttp": "aiohttp", 
        "motor": "motor", 
        "python-dotenv": "dotenv", # python-dotenv is imported as dotenv
        "py-yt": "py_yt"
    }
    
    missing = []
    for package, module in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
            
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing required packages...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            )
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies automatically: {e}")
            sys.exit(1)


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
