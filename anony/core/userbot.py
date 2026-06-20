"""
eXuCoDeR Music Bot - Userbot Client
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import Client

from anony import config, logger


class Userbot:
    """Manages assistant userbot clients for voice calls."""

    def __init__(self):
        self.clients = []
        clients = {"one": "SESSION1", "two": "SESSION2", "three": "SESSION3"}
        for key, string_key in clients.items():
            name = f"eXuCoDeR_UB{key[-1]}"
            session = getattr(config, string_key)
            if session:
                setattr(
                    self,
                    key,
                    Client(
                        name=name,
                        api_id=config.API_ID,
                        api_hash=config.API_HASH,
                        session_string=session,
                    ),
                )
            else:
                setattr(self, key, None)

    async def boot_client(self, num: int, ub: Client):
        """Boot a userbot client and perform setup."""
        clients_map = {1: self.one, 2: self.two, 3: self.three}
        client = clients_map[num]
        if not client:
            return

        await client.start()
        try:
            await client.send_message(
                config.LOGGER_ID,
                f"eXuCoDeR Assistant {num} Started"
            )
        except Exception:
            raise SystemExit(
                f"Assistant {num} failed to send message in log group."
            )

        client.id = client.me.id
        client.name = client.me.first_name
        client.username = client.me.username
        client.mention = client.me.mention
        self.clients.append(client)
        logger.info(f"Assistant {num} started as @{client.username}")

    async def boot(self):
        """Start all configured assistants."""
        for i, client in enumerate([self.one, self.two, self.three], 1):
            if client:
                await self.boot_client(i, client)

    async def exit(self):
        """Stop all assistants."""
        for client in [self.one, self.two, self.three]:
            if client:
                try:
                    await client.stop()
                except Exception:
                    pass
        logger.info("Assistants stopped.")
