from __future__ import annotations

import discord

from config import Settings


class BaseLayout(discord.ui.LayoutView):
    def __init__(self, settings: Settings, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.settings = settings

    def container(self, *items: discord.ui.Item) -> None:
        self.add_item(
            discord.ui.Container(
                *items,
                accent_color=discord.Color(self.settings.accent_color),
            )
        )


def help_view(settings: Settings) -> BaseLayout:
    view = BaseLayout(settings)
    view.container(
        discord.ui.TextDisplay(
            f"# {settings.emoji_brand} {settings.bot_name}\n"
            "Local, API-free image background removal."
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{settings.emoji_image} **.bgremove**\n"
            "Upload one image when prompted and receive a transparent PNG.\n\n"
            "🏓 **.ping**\n"
            "Show bot latency.\n\n"
            "ℹ️ **.about**\n"
            "Show creator and project information.\n\n"
            "❓ **.help**\n"
            "Show this panel."
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"{settings.emoji_success} Processing runs locally with a "
            "U²-Net-based open-source model."
        ),
    )
    return view


def about_view(settings: Settings) -> BaseLayout:
    view = BaseLayout(settings)
    view.container(
        discord.ui.TextDisplay(
            f"# {settings.emoji_brand} {settings.bot_name}\n"
            f"Version **{settings.bot_version}**"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            f"Built by **{settings.owner_name}**\n"
            f"{settings.emoji_github} GitHub\n{settings.owner_github}\n\n"
            f"{settings.emoji_website} Website\n{settings.owner_website}\n\n"
            f"Project source\n{settings.project_github}"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            "No commercial background-removal API is used. "
            "The model runs on the bot's own machine."
        ),
    )
    return view


def status_view(settings: Settings, title: str, body: str) -> BaseLayout:
    view = BaseLayout(settings)
    view.container(
        discord.ui.TextDisplay(f"# {title}"),
        discord.ui.Separator(),
        discord.ui.TextDisplay(body),
    )
    return view


def result_view(settings: Settings, filename: str, elapsed: float) -> BaseLayout:
    view = BaseLayout(settings)
    view.container(
        discord.ui.TextDisplay(
            f"# {settings.emoji_success} Background removed\n"
            f"File: **{filename}**\n"
            f"Processing time: **{elapsed:.2f}s**"
        ),
        discord.ui.Separator(),
        discord.ui.TextDisplay(
            "The transparent PNG is attached below. "
            "The bot does not intentionally persist the original image."
        ),
    )
    return view
