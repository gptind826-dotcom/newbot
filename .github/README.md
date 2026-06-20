# eXuCoDeR Music Bot

<p align="center">
  <img src="https://files.catbox.moe/zvziwk.jpg" alt="eXuCoDeR Music Bot" width="200">
</p>

<p align="center">
  <b>Professional Music Streaming Bot for Telegram</b>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square&logo=python"></a>
  <a href="https://github.com/gptind826-dotcom/newbot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square"></a>
  <a href="https://t.me/eXuCoDeR"><img src="https://img.shields.io/badge/Telegram-eXuCoDeR-blue.svg?style=flat-square&logo=telegram"></a>
</p>

---

## Overview

**eXuCoDeR Music Bot** is a professional, feature-rich Telegram music streaming bot designed for group voice chats. Built with Python, Pyrogram, and PyTgCalls, it delivers high-quality audio and video playback with automatic file cleanup, smart queue management, and a polished user experience.

## Features

- **High-Quality Streaming** - Low-latency audio/video playback via PyTgCalls
- **Multi-Platform Support** - YouTube, Spotify, Apple Music, SoundCloud, M3U8
- **Smart Queue Management** - Automatic queuing with position tracking
- **Auto-Cleanup** - Automatically deletes downloaded files after playback
- **Professional UI** - Clean inline keyboards and formatted messages
- **Multi-Language** - Support for 13 languages
- **Admin Controls** - Role-based access with sudo system
- **Playlist Support** - Queue entire YouTube playlists
- **Seek Functionality** - Jump to any position in the current track
- **Loop Mode** - Repeat tracks with configurable count
- **Thumbnail Generation** - Professional now-playing thumbnails

## Commands

### Play Commands
| Command | Description |
|---------|-------------|
| `/play <query>` | Play audio from YouTube/search |
| `/vplay <query>` | Play video from YouTube/search |
| `/playforce <query>` | Force play (skip queue) |
| `/vplayforce <query>` | Force play video |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/skip` | Skip current track |
| `/stop` | Stop playback |
| `/seek <seconds>` | Seek forward |
| `/seekback <seconds>` | Seek backward |
| `/loop <count/off>` | Set loop count |

### Utility Commands
| Command | Description |
|---------|-------------|
| `/queue` | Show current queue |
| `/ping` | Check bot status |
| `/stats` | Show statistics |
| `/settings` | Configure chat settings |
| `/lang` | Change language |

### Owner Commands
| Command | Description |
|---------|-------------|
| `/eval <code>` | Execute Python code |
| `/broadcast` | Broadcast message |
| `/addsudo <user>` | Add sudo user |
| `/rmsudo <user>` | Remove sudo user |
| `/restart` | Restart bot |
| `/logs` | Get log file |

## Deployment

### Prerequisites
- Python 3.10 or higher
- MongoDB database
- Telegram API credentials
- Bot token from [@BotFather](https://t.me/BotFather)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gptind826-dotcom/newbot.git
cd newbot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python app.py
```

### Heroku Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Docker

```bash
docker build -t exucoder-bot .
docker run --env-file .env exucoder-bot
```

## Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | Yes | Telegram API ID |
| `API_HASH` | Yes | Telegram API Hash |
| `BOT_TOKEN` | Yes | Bot token from @BotFather |
| `MONGO_URL` | Yes | MongoDB connection string |
| `LOGGER_ID` | Yes | Logger group/channel ID |
| `OWNER_ID` | Yes | Your Telegram user ID |
| `SESSION` | Yes | Pyrogram session string |
| `AUTO_DELETE` | No | Auto-delete files after playback (default: True) |
| `AUTO_LEAVE` | No | Auto-leave inactive chats (default: False) |
| `DURATION_LIMIT` | No | Max track duration in minutes (default: 60) |
| `QUEUE_LIMIT` | No | Max queue size (default: 20) |

## Project Structure

```
newbot/
|-- app.py                  # Main entry point
|-- config.py              # Configuration manager
|-- requirements.txt       # Python dependencies
|-- start                  # Start script
|-- .env.example           # Environment template
|-- anony/                 # Main package
|   |-- __init__.py        # Package init
|   |-- __main__.py        # Async main
|   |-- core/              # Core modules
|   |   |-- bot.py         # Bot client
|   |   |-- calls.py       # Voice call manager
|   |   |-- dir.py         # Directory setup
|   |   |-- lang.py        # Language manager
|   |   |-- mongo.py       # Database manager
|   |   |-- telegram.py    # Telegram utilities
|   |   |-- userbot.py     # Assistant clients
|   |   |-- youtube.py     # YouTube integration
|   |-- helpers/           # Helper modules
|   |   |-- _admins.py     # Admin checker
|   |   |-- _dataclass.py  # Data classes
|   |   |-- _exec.py       # Code execution
|   |   |-- _inline.py     # Inline keyboards
|   |   |-- _play.py       # Play decorator
|   |   |-- _queue.py      # Queue manager
|   |   |-- _thumbnails.py # Thumbnail generator
|   |   |-- _utilities.py  # Utility functions
|   |-- locales/           # Language files
|   |   |-- en.json        # English
|   |-- plugins/           # Command plugins
|   |   |-- play.py
|   |   |-- pause.py
|   |   |-- resume.py
|   |   |-- skip.py
|   |   |-- stop.py
|   |   |-- queue.py
|   |   |-- callbacks.py
|   |   |-- start.py
|   |   |-- ping.py
|   |   |-- stats.py
|   |   |-- auth.py
|   |   |-- active.py
|   |   |-- language.py
|   |   |-- loop.py
|   |   |-- seek.py
|   |   |-- eval.py
|   |   |-- broadcast.py
|   |   |-- blacklist.py
|   |   |-- sudoers.py
|   |   |-- restart.py
|   |   |-- misc.py
|   |   |-- iquery.py
|-- downloads/             # Downloaded files (auto-cleaned)
|-- cache/                 # Thumbnail cache
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Credits

- **Developer**: [eXuCoDeR](https://t.me/eXuCoDeR)
- **Framework**: [Pyrogram](https://github.com/pyrogram/pyrogram)
- **Voice Calls**: [PyTgCalls](https://github.com/pytgcalls/pytgcalls)

---

<p align="center">
  <b>eXuCoDeR Music Bot v4.0.0</b><br>
  <i>Professional Music Streaming for Telegram</i>
</p>
