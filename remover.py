from __future__ import annotations

import asyncio
import io
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, UnidentifiedImageError
from rembg import new_session, remove

from config import Settings

log = logging.getLogger(__name__)

# One inference at a time is deliberate: it prevents multiple ONNX sessions
# from competing for RAM/CPU and makes the bot predictable on small VPSes.
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="laabg-rembg")
_SESSION_LOCK = threading.Lock()
_SESSION = None
_SESSION_MODEL = None

# These are formats rembg's documented image pipeline can reliably decode.
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP", "TIFF", "HEIC", "HEIF"}


class ImageProcessingError(Exception):
    """A user-safe image processing error."""


def _get_session(settings: Settings):
    global _SESSION, _SESSION_MODEL

    with _SESSION_LOCK:
        if _SESSION is None or _SESSION_MODEL != settings.model:
            log.info("Loading local rembg model: %s", settings.model)
            os.environ["REMBG_HOME"] = settings.rembg_home
            _SESSION = new_session(settings.model)
            _SESSION_MODEL = settings.model
            log.info("Loaded rembg model: %s", settings.model)
        return _SESSION


def validate_image(data: bytes, settings: Settings) -> tuple[int, int, str]:
    if not data:
        raise ImageProcessingError("The uploaded file is empty.")

    max_bytes = settings.max_image_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise ImageProcessingError(
            f"That image is too large. The limit is {settings.max_image_mb} MB."
        )

    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            image_format = (image.format or "").upper()

            if width <= 0 or height <= 0:
                raise ImageProcessingError("The image dimensions are invalid.")

            if width * height > settings.max_image_pixels:
                raise ImageProcessingError(
                    f"That image has too many pixels. The limit is "
                    f"{settings.max_image_pixels:,} pixels."
                )

            if image_format not in SUPPORTED_FORMATS:
                raise ImageProcessingError(
                    "Unsupported image format. Use PNG, JPG/JPEG, WEBP, "
                    "BMP, TIFF, HEIC, or HEIF."
                )

            image.load()
            return width, height, image_format

    except ImageProcessingError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageProcessingError(
            "I couldn't read that file as a valid image."
        ) from exc


def _remove_sync(data: bytes, settings: Settings) -> bytes:
    session = _get_session(settings)

    # rembg returns PNG bytes when the input is bytes.
    output = remove(
        data,
        session=session,
        alpha_matting=settings.alpha_matting,
        decontaminate=settings.decontaminate,
        force_return_bytes=True,
    )
    if not output:
        raise ImageProcessingError("The model returned an empty image.")

    # Verify that the model really returned a valid PNG before Discord sees it.
    with Image.open(io.BytesIO(output)) as image:
        if image.format != "PNG":
            raise ImageProcessingError("The processor did not return a PNG.")
        image.verify()

    return bytes(output)


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
            "Processing timed out. Try a smaller image or use the lite model."
        ) from exc
    except ImageProcessingError:
        raise
    except Exception as exc:
        log.exception("Background removal failed")
        raise ImageProcessingError(
            "The local background-removal model failed. "
            "Check the bot console for the technical error."
        ) from exc
