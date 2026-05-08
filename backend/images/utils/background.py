import contextlib
import io
import importlib

import cv2
import numpy as np
from PIL import Image

_SESSION = None
_REMBG_LOADED = False
_REMBG_REMOVE = None
_REMBG_NEW_SESSION = None


def _load_rembg():
    global _REMBG_LOADED, _REMBG_REMOVE, _REMBG_NEW_SESSION

    if _REMBG_LOADED:
        return _REMBG_REMOVE, _REMBG_NEW_SESSION

    _REMBG_LOADED = True
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rembg_module = importlib.import_module("rembg")
        _REMBG_REMOVE = getattr(rembg_module, "remove", None)
        _REMBG_NEW_SESSION = getattr(rembg_module, "new_session", None)
    except BaseException:
        _REMBG_REMOVE = None
        _REMBG_NEW_SESSION = None

    return _REMBG_REMOVE, _REMBG_NEW_SESSION


def _get_session():
    global _SESSION

    remove, new_session = _load_rembg()
    if remove is None or new_session is None:
        return None

    if _SESSION is None:
        try:
            _SESSION = new_session("u2net")
        except Exception:
            return None

    return _SESSION


def _remove_background_with_grabcut(input_image):
    rgb_image = np.array(input_image.convert("RGB"))
    height, width = rgb_image.shape[:2]

    if height < 10 or width < 10:
        return input_image.convert("RGBA")

    mask = np.zeros((height, width), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    margin_x = max(4, width // 15)
    margin_y = max(4, height // 15)
    rect_width = max(1, width - (2 * margin_x))
    rect_height = max(1, height - (2 * margin_y))

    if rect_width <= 1 or rect_height <= 1:
        return input_image.convert("RGBA")

    rect = (margin_x, margin_y, rect_width, rect_height)

    try:
        cv2.grabCut(rgb_image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return input_image.convert("RGBA")

    foreground_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype("uint8")

    if not np.any(foreground_mask):
        return input_image.convert("RGBA")

    kernel = np.ones((3, 3), np.uint8)
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    foreground_mask = cv2.GaussianBlur(foreground_mask, (5, 5), 0)

    rgba_image = np.dstack((rgb_image, foreground_mask))
    return Image.fromarray(rgba_image, "RGBA")


def remove_background(image_file):
    """Remove the background from an image and return a transparent PNG."""
    try:
        image_file.seek(0)
        input_image = Image.open(image_file).convert("RGBA")
    except Exception as exc:
        raise RuntimeError("Please upload a valid image file.") from exc

    try:
        session = _get_session()
        remove, _ = _load_rembg()

        if session is not None and remove is not None:
            try:
                output_image = remove(input_image, session=session)
            except Exception:
                output_image = _remove_background_with_grabcut(input_image)
        else:
            output_image = _remove_background_with_grabcut(input_image)
    except Exception as exc:
        raise RuntimeError("Background removal failed for this image. Try a clearer photo or PNG.") from exc

    output_bytes = io.BytesIO()
    output_image.save(output_bytes, format="PNG")
    output_bytes.seek(0)
    return output_bytes
