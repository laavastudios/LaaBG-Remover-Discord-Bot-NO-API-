from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    raw = env_str(name, str(default))
    try:
        return int(raw, 0)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got {raw!r}") from exc


def env_bool(name: str, default: bool) -> bool:
    raw = env_str(name, str(default)).lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true/false, got {raw!r}")


@dataclass(frozen=True)
class Settings:
    token: str
    bot_name: str
    bot_version: str
    owner_name: str
    owner_github: str
    owner_website: str
    project_github: str
    owner_discord_id: int | None

    model: str
    alpha_matting: bool
    alpha_foreground_threshold: int
    alpha_background_threshold: int
    alpha_erode_size: int
    alpha_base_size: int

    max_image_mb: int
    max_image_pixels: int
    upload_timeout_seconds: int
    process_timeout_seconds: int

    accent_color: int

    emoji_brand: str
    emoji_success: str
    emoji_error: str
    emoji_loading: str
    emoji_image: str
    emoji_github: str
    emoji_website: str
    emoji_heart: str


def load_settings() -> Settings:
    token = env_str("DISCORD_TOKEN")
    if not token or token == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "DISCORD_TOKEN is missing. Copy .env.example to .env and add your bot token."
        )

    owner_id_raw = env_str("OWNER_DISCORD_ID")
    owner_id = int(owner_id_raw) if owner_id_raw else None

    return Settings(
        token=token,
        bot_name=env_str("BOT_NAME", "LaaBG Remover"),
        bot_version=env_str("BOT_VERSION", "1.0.0"),
        owner_name=env_str("OWNER_NAME", "LaavaBee"),
        owner_github=env_str("OWNER_GITHUB", "https://github.com/laavastudios"),
        owner_website=env_str("OWNER_WEBSITE", "https://laavastudios.live"),
        project_github=env_str(
            "PROJECT_GITHUB",
            "https://github.com/laavastudios/LaaBG-Remover-Discord-Bot-NO-API-",
        ),
        owner_discord_id=owner_id,
        model=env_str("BG_MODEL", "u2net"),
        alpha_matting=env_bool("BG_ALPHA_MATTING", True),
        alpha_foreground_threshold=env_int("BG_ALPHA_FOREGROUND_THRESHOLD", 240),
        alpha_background_threshold=env_int("BG_ALPHA_BACKGROUND_THRESHOLD", 10),
        alpha_erode_size=env_int("BG_ALPHA_ERODE_SIZE", 10),
        alpha_base_size=env_int("BG_ALPHA_BASE_SIZE", 1000),
        max_image_mb=env_int("MAX_IMAGE_MB", 20),
        max_image_pixels=env_int("MAX_IMAGE_PIXELS", 25_000_000),
        upload_timeout_seconds=env_int("UPLOAD_TIMEOUT_SECONDS", 120),
        process_timeout_seconds=env_int("PROCESS_TIMEOUT_SECONDS", 180),
        accent_color=env_int("ACCENT_COLOR", 0x7C3AED),
        emoji_brand=env_str("EMOJI_BRAND", "✨"),
        emoji_success=env_str("EMOJI_SUCCESS", "✅"),
        emoji_error=env_str("EMOJI_ERROR", "❌"),
        emoji_loading=env_str("EMOJI_LOADING", "⏳"),
        emoji_image=env_str("EMOJI_IMAGE", "🖼️"),
        emoji_github=env_str("EMOJI_GITHUB", "🐙"),
        emoji_website=env_str("EMOJI_WEBSITE", "🌐"),
        emoji_heart=env_str("EMOJI_HEART", "❤️"),
    )
