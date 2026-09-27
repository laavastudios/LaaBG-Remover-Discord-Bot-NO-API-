from __future__ import annotations

import discord

from config import Settings


class EmojiPack:
    def __init__(self, settings: Settings, guild: discord.Guild | None = None):
        self.settings = settings
        self.guild = guild
        self.apps = getattr(settings, "application_emojis", [])

    def resolve(self, value: str, fallback: str) -> str:
        value = (value or "").strip()
        if not value:
            return fallback
        if value.startswith("<:") or value.startswith("<a:"):
            return value

        if value.isdigit():
            eid = int(value)
            emoji = discord.utils.get(self.guild.emojis, id=eid) if self.guild else None
            if emoji:
                return str(emoji)
            emoji = discord.utils.get(self.apps, id=eid)
            if emoji:
                return str(emoji)

        if self.guild:
            emoji = discord.utils.get(self.guild.emojis, name=value)
            if emoji:
                return str(emoji)

        emoji = discord.utils.get(self.apps, name=value)
        return str(emoji) if emoji else fallback

    def __getattr__(self, name: str) -> str:
        values = {
            "brand": ("emoji_brand", "✨"),
            "success": ("emoji_success", "✅"),
            "error": ("emoji_error", "❌"),
            "loading": ("emoji_loading", "⏳"),
            "image": ("emoji_image", "🖼️"),
            "github": ("emoji_github", "🐙"),
            "website": ("emoji_website", "🌐"),
            "heart": ("emoji_heart", "❤️"),
            "ping": ("emoji_ping", "🏓"),
            "info": ("emoji_info", "ℹ️"),
            "help": ("emoji_help", "❓"),
            "sparkle": ("emoji_sparkle", "✨"),
        }
        attr, fallback = values[name]
        return self.resolve(getattr(self.settings, attr, ""), fallback)


class BaseLayout(discord.ui.LayoutView):
    def __init__(self, settings: Settings, guild: discord.Guild | None = None):
        super().__init__(timeout=180)
        self.settings = settings
        self.e = EmojiPack(settings, guild)

    def container(self, *items: discord.ui.Item):
        self.add_item(discord.ui.Container(
            *items,
            accent_color=discord.Color(self.settings.accent_color),
        ))

    def links(self):
        row = discord.ui.ActionRow()
        row.add_item(discord.ui.Button(
            label="GitHub", emoji=self.e.github,
            style=discord.ButtonStyle.link, url=self.settings.project_github,
        ))
        row.add_item(discord.ui.Button(
            label="Website", emoji=self.e.website,
            style=discord.ButtonStyle.link, url=self.settings.owner_website,
        ))
        return row


def help_view(settings, guild=None):
    view = BaseLayout(settings, guild)
    e = view.e
    view.container(
        discord.ui.TextDisplay(
            f"# {e.brand} {settings.bot_name}\n"
            "Premium-style background removal. Local. API-free."
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"### {e.image} Background Removal\n"
            "**.bgremove**\n"
            "Upload one image when prompted. LaaBG removes the background "
            "locally and returns a transparent PNG."
        ),
        discord.ui.TextDisplay(
            f"### {e.ping} Commands\n"
            "**.ping** — latency\n"
            "**.about** — creator and project\n"
            "**.help** — this panel"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{e.success} U²-Net local inference  •  PNG output  •  no removal API"
        ),
        view.links(),
    )
    return view


def about_view(settings, guild=None):
    view = BaseLayout(settings, guild)
    e = view.e
    view.container(
        discord.ui.TextDisplay(
            f"# {e.brand} {settings.bot_name}\n"
            f"Version **{settings.bot_version}** · Built by **{settings.owner_name}**"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{e.heart} **Laava Studios**\n"
            "Building useful things that should exist.\n\n"
            f"{e.github} **GitHub**\n{settings.owner_github}\n\n"
            f"{e.website} **Website**\n{settings.owner_website}"
        ),
        discord.ui.TextDisplay(
            f"{e.image} **Local processing**\n"
            "The image is processed by the bot's local U²-Net pipeline. "
            "No commercial background-removal API is required."
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{e.sparkle} **Source**\n{settings.project_github}"
        ),
        view.links(),
    )
    return view


def status_view(settings, title, body, guild=None):
    view = BaseLayout(settings, guild)
    view.container(
        discord.ui.TextDisplay(f"# {title}"),
        discord.ui.Separator(),
        discord.ui.TextDisplay(body),
    )
    return view


def result_view(settings, filename, elapsed, guild=None):
    view = BaseLayout(settings, guild)
    e = view.e
    view.container(
        discord.ui.TextDisplay(
            f"# {e.success} Background removed\n"
            f"File: **{filename}**\n"
            f"Processing: **{elapsed:.2f}s**"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{e.image} Your transparent PNG is attached below.\n"
            "The bot does not intentionally persist the original image."
        ),
        view.links(),
    )
    return view
