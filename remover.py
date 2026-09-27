from __future__ import annotations

import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, UnidentifiedImageError
from backgroundremover.bg import remove

from config import Settings

log = logging.getLogger(__name__)
_EXECUTOR = ThreadPoolExecutor(max_workers=1)

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP", "TIFF", "GIF", "HEIC", "HEIF"}


class ImageProcessingError(Exception):
    pass


def validate_image(data: bytes, settings: Settings) -> None:
    if not data:
        raise ImageProcessingError("The uploaded file is empty.")

    max_bytes = settings.max_image_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise ImageProcessingError(
            f"The image is too large. Limit: {settings.max_image_mb} MB."
        )

    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.width * image.height > settings.max_image_pixels:
                raise ImageProcessingError(
                    f"The image has too many pixels. Limit: "
                    f"{settings.max_image_pixels:,} pixels."
                )
            if (image.format or "").upper() not in SUPPORTED_FORMATS:
                raise ImageProcessingError("Unsupported image format.")
            image.load()
    except ImageProcessingError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageProcessingError("The uploaded file is not a valid image.") from exc


def _remove_sync(data: bytes, settings: Settings) -> bytes:
    return remove(
        data,
        model_name=settings.model,
        alpha_matting=settings.alpha_matting,
        alpha_matting_foreground_threshold=settings.alpha_foreground_threshold,
        alpha_matting_background_threshold=settings.alpha_background_threshold,
        alpha_matting_erode_structure_size=settings.alpha_erode_size,
        alpha_matting_base_size=settings.alpha_base_size,
    )


async def remove_background(data: bytes, settings: Settings) -> bytes:
    validate_image(data, settings)
    loop = asyncio.get_running_loop()

    try:
        return await asyncio.wait_for(
            loop.run_in_executor(_EXECUTOR, _remove_sync, data, settings),
            timeout=settings.process_timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        raise ImageProcessingError(
            "Processing timed out. Try a smaller image."
        ) from exc
    except ImageProcessingError:
        raise
    except Exception as exc:
        log.exception("Background removal failed")
        raise ImageProcessingError(
            "The local model failed while processing this image."
        ) from exc
