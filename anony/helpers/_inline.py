"""
eXuCoDeR Music Bot - Inline Keyboards
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.

Professional UI/UX with modern button layouts.
"""

from pyrogram import types

from anony import app, config, lang
from anony.core.lang import lang_codes


class Inline:
    """Professional inline keyboard builder for eXuCoDeR Music Bot."""

    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text: str) -> types.InlineKeyboardMarkup:
        """Cancel download button."""
        return self.ikm([[self.ikb(text=text, callback_data="cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        """Player control buttons with professional layout."""
        keyboard = []

        # Status/timer display row
        if status:
            keyboard.append([
                self.ikb(
                    text=f"{status}",
                    callback_data=f"controls status {chat_id}"
                )
            ])
        elif timer:
            keyboard.append([
                self.ikb(
                    text=f"{timer}",
                    callback_data=f"controls status {chat_id}"
                )
            ])

        if not remove:
            # Professional control buttons
            keyboard.append([
                self.ikb(text="Resume", callback_data=f"controls resume {chat_id}"),
                self.ikb(text="Pause", callback_data=f"controls pause {chat_id}"),
                self.ikb(text="Replay", callback_data=f"controls replay {chat_id}"),
            ])
            keyboard.append([
                self.ikb(text="Skip", callback_data=f"controls skip {chat_id}"),
                self.ikb(text="Stop", callback_data=f"controls stop {chat_id}"),
            ])

        return self.ikm(keyboard)

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        """Help menu buttons with professional layout."""
        if back:
            rows = [[
                self.ikb(text=_lang.get("back", "Back"), callback_data="help back"),
                self.ikb(text=_lang.get("close", "Close"), callback_data="help close"),
            ]]
        else:
            cbs = ["admins", "auth", "blist", "lang", "ping", "play",
                   "queue", "stats", "sudo"]
            btn_list = [
                self.ikb(
                    text=_lang.get(f"help_{i}", cb.title()),
                    callback_data=f"help {cb}"
                )
                for i, cb in enumerate(cbs)
            ]
            rows = [btn_list[i:i + 3] for i in range(0, len(btn_list), 3)]

        return self.ikm(rows)

    def lang_markup(self, _lang_code: str) -> types.InlineKeyboardMarkup:
        """Language selection buttons."""
        langs = lang.get_languages()
        btn_list = [
            self.ikb(
                text=f"{name} ({code}) {'✓' if code == _lang_code else ''}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        rows = [btn_list[i:i + 2] for i in range(0, len(btn_list), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        """Ping info button linking to support."""
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        """Button to play a queued item immediately."""
        return self.ikm([[
            self.ikb(
                text=_text,
                callback_data=f"controls force {chat_id} {item_id}"
            )
        ]])

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        """Queue control button."""
        action = "pause" if playing else "resume"
        return self.ikm([[
            self.ikb(text=_text, callback_data=f"controls {action} {chat_id} q")
        ]])

    def settings_markup(
        self,
        lang_dict: dict,
        admin_only: bool,
        cmd_delete: bool,
        language: str,
        chat_id: int,
    ) -> types.InlineKeyboardMarkup:
        """Settings panel with professional layout."""
        return self.ikm([
            [
                self.ikb(
                    text=f"{lang_dict.get('play_mode', 'Admin Only')} >",
                    callback_data="settings",
                ),
                self.ikb(
                    text=str(admin_only),
                    callback_data="settings play",
                ),
            ],
            [
                self.ikb(
                    text=f"{lang_dict.get('cmd_delete', 'Cmd Delete')} >",
                    callback_data="settings",
                ),
                self.ikb(
                    text=str(cmd_delete),
                    callback_data="settings delete",
                ),
            ],
            [
                self.ikb(
                    text=f"{lang_dict.get('language', 'Language')} >",
                    callback_data="settings",
                ),
                self.ikb(
                    text=lang_codes.get(language, language),
                    callback_data="language",
                ),
            ],
        ])

    def start_key(
        self, lang_dict: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        """Start message buttons with professional layout."""
        rows = [
            [self.ikb(
                text=lang_dict.get("add_me", "Add to Group"),
                url=f"https://t.me/{app.username}?startgroup=true",
            )],
            [self.ikb(
                text=lang_dict.get("help", "Help"),
                callback_data="help",
            )],
            [
                self.ikb(
                    text=lang_dict.get("support", "Support"),
                    url=config.SUPPORT_CHAT,
                ),
                self.ikb(
                    text=lang_dict.get("channel", "Channel"),
                    url=config.SUPPORT_CHANNEL,
                ),
            ],
        ]
        if private:
            rows.append([
                self.ikb(
                    text="Developer",
                    url="https://t.me/eXuCoDeR",
                )
            ])
        else:
            rows.append([
                self.ikb(
                    text=lang_dict.get("language", "Language"),
                    callback_data="language",
                )
            ])
        return self.ikm(rows)

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        """YouTube link buttons."""
        return self.ikm([[
            self.ikb(text="Copy Link", copy_text=link),
            self.ikb(text="Watch on YouTube", url=link),
        ]])
