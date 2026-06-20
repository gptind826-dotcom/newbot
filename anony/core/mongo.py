"""
eXuCoDeR Music Bot - MongoDB Database Manager
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from motor.motor_asyncio import AsyncIOMotorClient

from anony import config, logger


class MongoDB:
    """MongoDB database manager for bot data persistence."""

    def __init__(self):
        self.client = None
        self.db = None
        self.chats = None
        self.users = None
        self.sudoers_collection = None
        self.blacklist_collection = None
        self.active_calls_collection = None
        self.admins_cache = {}
        self.active_calls = set()
        self.notified = set()
        self.blacklisted = set()
        self.cmd_delete_chats = set()
        self.play_mode_chats = set()
        self.language_cache = {}

    async def connect(self):
        """Connect to MongoDB database."""
        try:
            self.client = AsyncIOMotorClient(
                config.MONGO_URL,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client["exucoder_bot"]
            self.chats = self.db["chats"]
            self.users = self.db["users"]
            self.sudoers_collection = self.db["sudoers"]
            self.blacklist_collection = self.db["blacklist"]
            self.active_calls_collection = self.db["active_calls"]

            # Load blacklisted items into memory
            async for item in self.blacklist_collection.find():
                self.blacklisted.add(item["_id"])

            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise SystemExit(f"Failed to connect to MongoDB: {e}")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    # === Chats ===
    async def add_chat(self, chat_id: int):
        """Add a chat to the database."""
        await self.chats.update_one(
            {"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True
        )

    async def is_chat(self, chat_id: int) -> bool:
        """Check if a chat exists in the database."""
        return await self.chats.find_one({"_id": chat_id}) is not None

    # === Users ===
    async def add_user(self, user_id: int):
        """Add a user to the database."""
        await self.users.update_one(
            {"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True
        )

    async def is_user(self, user_id: int) -> bool:
        """Check if a user exists in the database."""
        return await self.users.find_one({"_id": user_id}) is not None

    # === Sudoers ===
    async def add_sudoer(self, user_id: int):
        """Add a sudo user."""
        await self.sudoers_collection.update_one(
            {"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True
        )

    async def remove_sudoer(self, user_id: int):
        """Remove a sudo user."""
        await self.sudoers_collection.delete_one({"_id": user_id})

    async def get_sudoers(self) -> list:
        """Get all sudo users."""
        cursor = self.sudoers_collection.find()
        return [doc["_id"] async for doc in cursor]

    # === Blacklist ===
    async def add_blacklist(self, chat_id: int):
        """Add a chat/user to blacklist."""
        await self.blacklist_collection.update_one(
            {"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True
        )
        self.blacklisted.add(chat_id)

    async def remove_blacklist(self, chat_id: int):
        """Remove a chat/user from blacklist."""
        await self.blacklist_collection.delete_one({"_id": chat_id})
        self.blacklisted.discard(chat_id)

    async def get_blacklisted(self) -> set:
        """Get all blacklisted IDs."""
        return self.blacklisted

    # === Active Calls ===
    async def add_call(self, chat_id: int):
        """Mark a chat as having an active call."""
        self.active_calls.add(chat_id)
        await self.active_calls_collection.update_one(
            {"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True
        )

    async def remove_call(self, chat_id: int):
        """Remove a chat from active calls."""
        self.active_calls.discard(chat_id)
        await self.active_calls_collection.delete_one({"_id": chat_id})

    async def get_call(self, chat_id: int) -> bool:
        """Check if a chat has an active call."""
        return chat_id in self.active_calls

    async def get_active_calls(self) -> list:
        """Get all active calls."""
        cursor = self.active_calls_collection.find()
        return [doc["_id"] async for doc in cursor]

    # === Admins Cache ===
    async def get_admins(self, chat_id: int) -> list:
        """Get cached admin list for a chat."""
        return self.admins_cache.get(chat_id, [])

    async def set_admins(self, chat_id: int, admins: list):
        """Cache admin list for a chat."""
        self.admins_cache[chat_id] = admins

    # === Play Mode ===
    async def get_play_mode(self, chat_id: int) -> bool:
        """Get admin-only play mode for a chat."""
        return chat_id in self.play_mode_chats

    async def toggle_play_mode(self, chat_id: int):
        """Toggle admin-only play mode."""
        if chat_id in self.play_mode_chats:
            self.play_mode_chats.discard(chat_id)
        else:
            self.play_mode_chats.add(chat_id)

    # === Command Delete ===
    async def get_cmd_delete(self, chat_id: int) -> bool:
        """Get command delete setting for a chat."""
        return chat_id in self.cmd_delete_chats

    async def toggle_cmd_delete(self, chat_id: int):
        """Toggle command delete setting."""
        if chat_id in self.cmd_delete_chats:
            self.cmd_delete_chats.discard(chat_id)
        else:
            self.cmd_delete_chats.add(chat_id)

    # === Language ===
    async def get_lang(self, chat_id: int) -> str:
        """Get language code for a chat."""
        return self.language_cache.get(chat_id, "en")

    async def set_lang(self, chat_id: int, lang_code: str):
        """Set language code for a chat."""
        self.language_cache[chat_id] = lang_code

    # === Assistant Management ===
    async def get_assistant(self, chat_id: int):
        """Get an assistant client for a chat."""
        from anony import userbot
        if not userbot.clients:
            return None
        # Simple round-robin assignment
        idx = hash(chat_id) % len(userbot.clients)
        return userbot.clients[idx]

    async def get_client(self, chat_id: int):
        """Get a client for the chat (for joining)."""
        from anony import userbot
        if not userbot.clients:
            return None
        idx = hash(chat_id) % len(userbot.clients)
        return userbot.clients[idx]

    # === Playing State ===
    async def playing(self, chat_id: int, paused: bool = False):
        """Update playing state."""
        pass  # Can be extended for state tracking

    # === Loop ===
    async def get_loop(self, chat_id: int) -> int:
        """Get loop count for a chat."""
        return 0  # Can be extended

    async def set_loop(self, chat_id: int, count: int):
        """Set loop count for a chat."""
        pass  # Can be extended

    # === Auth ===
    async def add_auth(self, chat_id: int, user_id: int):
        """Add authorized user to a chat."""
        pass  # Can be extended

    async def remove_auth(self, chat_id: int, user_id: int):
        """Remove authorized user from a chat."""
        pass  # Can be extended

    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        """Check if a user is authorized in a chat."""
        return False  # Can be extended

    # === Logger ===
    async def is_logger(self) -> bool:
        """Check if logger is enabled."""
        return True  # Always log
