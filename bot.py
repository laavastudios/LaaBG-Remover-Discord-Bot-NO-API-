from __future__ import annotations

import asyncio
import io
import logging
import time
from pathlib import PurePosixPath

import aiohttp
import discord
from discord.ext import commands

from config import Settings, load_settings
from remover import ImageProcessingError, remove_background
from ui import EmojiPack, about_view, help_view, result_view, status_view

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("laabg")
settings: Settings = load_settings()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None,
    case_insensitive=True,
)


def is_image_attachment(attachment: discord.Attachment) -> bool:
    content_type = (attachment.content_type or "").lower()
    suffix = PurePosixPath(attachment.filename).suffix.lower()
    return content_type.startswith("image/") or suffix in {
        ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"
    }


async def download_attachment(attachment: discord.Attachment) -> bytes:
    timeout = aiohttp.ClientTimeout(total=settings.upload_timeout_seconds)
    max_bytes = settings.max_image_mb * 1024 * 1024

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers={"User-Agent": "LaaBG-Remover/1.1"},
    ) as session:
        async with session.get(attachment.url) as response:
            if response.status != 200:
                raise ImageProcessingError(
                    f"Discord returned HTTP {response.status} while downloading the image."
                )

            if response.content_length and response.content_length > max_bytes:
                raise ImageProcessingError(
                    f"The image is too large. Limit: {settings.max_image_mb} MB."
                )

            data = bytearray()
            async for chunk in response.content.iter_chunked(1024 * 1024):
                data.extend(chunk)
                if len(data) > max_bytes:
                    raise ImageProcessingError(
                        f"The image is too large. Limit: {settings.max_image_mb} MB."
                    )
            return bytes(data)


async def send_view(channel, view):
    return await channel.send(view=view)


@bot.event
async def on_ready():
    try:
        settings.application_emojis = await bot.fetch_application_emojis()
        log.info("Loaded %d application emojis.", len(settings.application_emojis))
    except discord.HTTPException:
        settings.application_emojis = []
        log.exception("Application emoji fetch failed; fallbacks remain available.")

    log.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "?")
    log.info("Serving %d guild(s)", len(bot.guilds))


@bot.command(name="help")
async def help_command(ctx):
    await send_view(ctx.channel, help_view(settings, ctx.guild))


@bot.command(name="about")
async def about_command(ctx):
    await send_view(ctx.channel, about_view(settings, ctx.guild))


@bot.command(name="ping")
async def ping_command(ctx):
    latency_ms = round(bot.latency * 1000)
    await send_view(
        ctx.channel,
        status_view(
            settings,
            f"{EmojiPack(settings, ctx.guild).ping} Pong — {latency_ms} ms",
            "WebSocket latency measured successfully.",
            ctx.guild,
        ),
    )


@bot.command(name="bgremove")
@commands.cooldown(1, 3.0, commands.BucketType.user)
async def bgremove_command(ctx):
    await send_view(
        ctx.channel,
        status_view(
            settings,
            f"{EmojiPack(settings, ctx.guild).image} Upload an image",
            "Send one image in this channel within "
            f"{settings.upload_timeout_seconds} seconds.\n\n"
            f"Maximum size: {settings.max_image_mb} MB.",
            ctx.guild,
        ),
    )

    def check(message):
        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and bool(message.attachments)
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=settings.upload_timeout_seconds,
            check=check,
        )
    except asyncio.TimeoutError:
        await send_view(
            ctx.channel,
            status_view(
                settings,
                f"{EmojiPack(settings, ctx.guild).error} Timed out",
                "No image was uploaded. Run .bgremove again.",
                ctx.guild,
            ),
        )
        return

    attachment = next(
        (a for a in message.attachments if is_image_attachment(a)),
        None,
    )

    if attachment is None:
        await send_view(
            ctx.channel,
            status_view(
                settings,
                f"{EmojiPack(settings, ctx.guild).error} Not an image",
                "Please upload a valid image and run .bgremove again.",
                ctx.guild,
            ),
        )
        return

    await send_view(
        ctx.channel,
        status_view(
            settings,
            f"{EmojiPack(settings, ctx.guild).loading} Processing",
            "Running local background removal. The first run may be slower "
            "while the model is prepared.",
            ctx.guild,
        ),
    )

    started = time.perf_counter()

    try:
        raw = await download_attachment(attachment)
        result = await remove_background(raw, settings)
        filename = f"{PurePosixPath(attachment.filename).stem}_no_bg.png"

        await ctx.channel.send(
            view=result_view(
                settings,
                filename,
                time.perf_counter() - started,
                ctx.guild,
            ),
            file=discord.File(io.BytesIO(result), filename=filename),
        )
    except ImageProcessingError as exc:
        await send_view(
            ctx.channel,
            status_view(
                settings,
                f"{EmojiPack(settings, ctx.guild).error} Could not process image",
                str(exc),
                ctx.guild,
            ),
        )
    except Exception:
        log.exception("Unexpected background-removal failure")
        await send_view(
            ctx.channel,
            status_view(
                settings,
                f"{EmojiPack(settings, ctx.guild).error} Unexpected error",
                "Something went wrong. Check the bot console for details.",
                ctx.guild,
            ),
        )


@bgremove_command.error
async def bgremove_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await send_view(
            ctx.channel,
            status_view(
                settings,
                f"{EmojiPack(settings, ctx.guild).error} Slow down",
                f"Try .bgremove again in {error.retry_after:.1f}s.",
                ctx.guild,
            ),
        )
        return
    log.exception("bgremove command error", exc_info=error)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CommandOnCooldown):
        return
    log.exception("Unhandled command error", exc_info=error)


if __name__ == "__main__":
    bot.run(settings.token)
