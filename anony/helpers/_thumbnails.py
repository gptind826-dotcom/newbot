"""
eXuCoDeR Music Bot - Thumbnail Generator
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps)

from anony import config, logger
from anony.helpers import Track


class Thumbnail:
    """Generate professional thumbnails for now playing tracks."""

    def __init__(self):
        self.rect = (914, 514)
        self.fill = (255, 255, 255)
        self.mask = Image.new("L", self.rect, 0)
        self.font1 = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 30)
        self.font2 = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 30)
        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """Initialize aiohttp session."""
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        """Download thumbnail image from URL."""
        async with self.session.get(url) as resp:
            with open(output_path, "wb") as f:
                f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        """Generate a professional thumbnail for a track."""
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"

            # Return cached thumbnail
            if os.path.exists(output):
                return output

            # Download thumbnail
            if not song.thumbnail:
                return config.DEFAULT_THUMB

            await self.save_thumb(temp, song.thumbnail)

            # Process image
            thumb = Image.open(temp).convert("RGBA").resize(
                size, Image.Resampling.LANCZOS,
            )
            blur = thumb.filter(ImageFilter.GaussianBlur(25))
            image = ImageEnhance.Brightness(blur).enhance(0.40)

            # Add rounded rectangle overlay
            _rect = ImageOps.fit(
                thumb, self.rect,
                method=Image.LANCZOS, centering=(0.5, 0.5),
            )
            ImageDraw.Draw(self.mask).rounded_rectangle(
                (0, 0, self.rect[0], self.rect[1]),
                radius=15, fill=255,
            )
            _rect.putalpha(self.mask)
            image.paste(_rect, (183, 30), _rect)

            # Draw text
            draw = ImageDraw.Draw(image)
            channel = song.channel_name[:25] if song.channel_name else "Unknown"
            views = song.view_count or ""
            title = song.title[:50] if song.title else "Unknown"
            duration = song.duration or "00:00"

            draw.text(
                xy=(50, 560),
                text=f"{channel} | {views}",
                font=self.font2, fill=self.fill,
            )
            draw.text((50, 600), title, font=self.font1, fill=self.fill)
            draw.text((40, 650), "0:01", font=self.font1)
            draw.line(
                [(140, 670), (1160, 670)],
                fill=self.fill, width=5, joint="curve"
            )
            draw.text((1185, 650), duration, font=self.font1, fill=self.fill)

            # Add branding
            draw.text(
                (50, 30),
                "eXuCoDeR Music",
                font=ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 20),
                fill=(200, 200, 200),
            )

            image.save(output)

            # Clean up temp file
            try:
                os.remove(temp)
            except Exception:
                pass

            return output
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {e}")
            return config.DEFAULT_THUMB
