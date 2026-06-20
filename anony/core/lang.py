"""
eXuCoDeR Music Bot - Language Manager
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import json
from functools import wraps
from pathlib import Path

from pyrogram import errors

from anony import db, logger

lang_codes = {
    "ar": "\u0627\u0644\u0639\u0631\u0628\u064a\u0629",
    "de": "Deutsch",
    "en": "English",
    "es": "Espa\u00f1ol",
    "fr": "Fran\u00e7ais",
    "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",
    "ja": "\u65e5\u672c\u8a9e",
    "my": "\u1019\u103c\u1014\u103a\u1019\u102c\u1018\u102f\u101e\u102c",
    "pa": "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",
    "pt": "Portugu\u00eas",
    "ru": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439",
    "tr": "T\u00fcrk\u00e7e",
    "zh": "\u4e2d\u6587"
}


class Language:
    """Language manager for multilingual support."""

    def __init__(self):
        self.lang_codes = lang_codes
        self.lang_dir = Path("anony/locales")
        self.languages = self.load_files()

    def load_files(self):
        """Load all language JSON files."""
        languages = {}
        lang_files = {
            file.stem: file for file in self.lang_dir.glob("*.json")
        }
        for lang_code, lang_file in lang_files.items():
            with open(lang_file, "r", encoding="utf-8") as file:
                languages[lang_code] = json.load(file)
        logger.info(f"Loaded languages: {', '.join(languages.keys())}")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        """Get language dictionary for a chat."""
        lang_code = await db.get_lang(chat_id)
        return self.languages.get(lang_code, self.languages.get("en"))

    def get_languages(self) -> dict:
        """Get available languages."""
        files = {f.stem for f in self.lang_dir.glob("*.json")}
        return {
            code: self.lang_codes[code]
            for code in sorted(files) if code in self.lang_codes
        }

    def language(self):
        """Decorator to attach language to handler context."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                message_obj = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                if not message_obj or not message_obj.from_user:
                    return

                if hasattr(message_obj, "chat"):
                    chat = message_obj.chat
                elif hasattr(message_obj, "message"):
                    chat = message_obj.message.chat
                else:
                    return

                if chat.id in db.blacklisted:
                    logger.info(f"Chat {chat.id} is blacklisted, leaving...")
                    return await chat.leave()

                lang_code = await db.get_lang(chat.id)
                lang_dict = self.languages.get(
                    lang_code, self.languages.get("en", {})
                )

                setattr(message_obj, "lang", lang_dict)
                try:
                    return await func(*args, **kwargs)
                except (
                    errors.ChannelPrivate,
                    errors.MessageIdInvalid,
                    errors.MessageNotModified,
                ):
                    return
                except (
                    errors.Forbidden,
                    errors.ChatWriteForbidden,
                ):
                    return
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    return

            return wrapper
        return decorator
