from __future__ import annotations

import os
from dataclasses import dataclass, field

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


@dataclass
class Settings:
    token: str
    bot_name: str
    bot_version: str
    owner_name: str
    owner_github: str
    owner_website: str
    project_github: str
    owner_discord_id: int | None

    # rembg local ONNX model.
    # birefnet-general is the quality-oriented general model.
    # birefnet-general-lite is lighter/faster.
    # birefnet-portrait is intended for portraits.
    model: str
    rembg_home: str
    alpha_matting: bool
    decontaminate: bool

    max_image_mb: int
    max_image_pixels: int
    max_output_mb: int
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
    emoji_ping: str
    emoji_info: str
    emoji_help: str
    emoji_sparkle: str

    application_emojis: list = field(default_factory=list)


def load_settings() -> Settings:
    token = env_str("DISCORD_TOKEN")
    if not token or token == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "DISCORD_TOKEN is missing. Copy .env.example to .env and add your bot token."
        )

    owner_id_raw = env_str("OWNER_DISCORD_ID")
    owner_id = int(owner_id_raw) if owner_id_raw else None

    model = env_str("BG_MODEL", "birefnet-general")
    allowed_models = {
        "birefnet-general",
        "birefnet-general-lite",
        "birefnet-portrait",
        "u2net",
        "u2netp",
        "u2net_human_seg",
        "isnet-general-use",
        "isnet-anime",
    }
    if model not in allowed_models:
        raise RuntimeError(
            f"Unsupported BG_MODEL={model!r}. Choose one of: "
            + ", ".join(sorted(allowed_models))
        )

    max_mb = env_int("MAX_IMAGE_MB", 20)
    max_pixels = env_int("MAX_IMAGE_PIXELS", 25_000_000)
    max_output_mb = env_int("MAX_OUTPUT_MB", 24)
    if max_mb < 1 or max_mb > 25:
        raise RuntimeError("MAX_IMAGE_MB must be between 1 and 25.")
    if max_pixels < 100_000:
        raise RuntimeError("MAX_IMAGE_PIXELS is unrealistically small.")
    if max_output_mb < 1 or max_output_mb > 25:
        raise RuntimeError("MAX_OUTPUT_MB must be between 1 and 25.")

    return Settings(
        token=token,
        bot_name=env_str("BOT_NAME", "LaaBG Remover"),
        bot_version=env_str("BOT_VERSION", "2.0.0"),
        owner_name=env_str("OWNER_NAME", "LaavaBee"),
        owner_github=env_str("OWNER_GITHUB", "https://github.com/laavastudios"),
        owner_website=env_str("OWNER_WEBSITE", "https://laavastudios.live"),
        project_github=env_str(
            "PROJECT_GITHUB",
            "https://github.com/laavastudios/LaaBG-Remover-Discord-Bot-NO-API-",
        ),
        owner_discord_id=owner_id,
        model=model,
        rembg_home=env_str("REMBG_HOME", "./models"),
        alpha_matting=env_bool("BG_ALPHA_MATTING", False),
        decontaminate=env_bool("BG_DECONTAMINATE", True),
        max_image_mb=max_mb,
        max_image_pixels=max_pixels,
        max_output_mb=max_output_mb,
        upload_timeout_seconds=env_int("UPLOAD_TIMEOUT_SECONDS", 120),
        process_timeout_seconds=env_int("PROCESS_TIMEOUT_SECONDS", 300),
        accent_color=env_int("ACCENT_COLOR", 0x7C3AED),
        emoji_brand=env_str("EMOJI_BRAND", "✨"),
        emoji_success=env_str("EMOJI_SUCCESS", "✅"),
        emoji_error=env_str("EMOJI_ERROR", "❌"),
        emoji_loading=env_str("EMOJI_LOADING", "⏳"),
        emoji_image=env_str("EMOJI_IMAGE", "🖼️"),
        emoji_github=env_str("EMOJI_GITHUB", "🐙"),
        emoji_website=env_str("EMOJI_WEBSITE", "🌐"),
        emoji_heart=env_str("EMOJI_HEART", "❤️"),
        emoji_ping=env_str("EMOJI_PING", "🏓"),
        emoji_info=env_str("EMOJI_INFO", "ℹ️"),
        emoji_help=env_str("EMOJI_HELP", "❓"),
        emoji_sparkle=env_str("EMOJI_SPARKLE", "✨"),
    )
