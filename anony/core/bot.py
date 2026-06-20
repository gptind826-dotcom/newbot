"""
eXuCoDeR Music Bot - Bot Client
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import pyrogram

from anony import config, logger


class Bot(pyrogram.Client):
    """Main bot client with eXuCoDeR branding."""

    def __init__(self):
        super().__init__(
            name="exucoder",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(
                is_disabled=True
            ),
        )
        self.owner = config.OWNER_ID
        self.logger = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def boot(self):
        """
        Start the bot and perform initial setup.

        Raises:
            SystemExit: If the bot fails to access the log group
                       or is not an administrator.
        """
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                self.logger,
                "eXuCoDeR Music Bot Started Successfully"
            )
            get = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(
                f"Bot failed to access log group: {self.logger}\n"
                f"Reason: {ex}"
            )

        if get.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit(
                "Please promote the bot as admin in the logger group."
            )
        logger.info(f"Bot started as @{self.username}")

    async def exit(self):
        """Stop the bot gracefully."""
        await super().stop()
        logger.info("Bot stopped.")
