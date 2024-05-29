import base64
import io
import logging
import requests
from PIL import Image, UnidentifiedImageError
from django.conf import settings

logger = logging.getLogger(__name__)


def resize_image(image_bytes: bytes) -> bytes:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail((1024, 1024))
        image_io = io.BytesIO()
        image.save(image_io, format=image.format)
        return image_io.getvalue()
    except UnidentifiedImageError as e:
        logger.error(f"Error resizing image: {e}")
        raise


def remove_background(image_bytes: bytes) -> bytes:
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': io.BytesIO(image_bytes)},
            data={'size': 'auto'},
            headers={'X-Api-Key': settings.REMOVE_BG_API_KEY}
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.error(f"Error removing background: {e}")
        raise


def process_image_bytes(image_bytes: bytes) -> str:
    try:
        image_io = io.BytesIO(image_bytes)
        image = Image.open(image_io)
        if image.format not in ["JPEG", "PNG", "GIF"]:
            raise ValueError("Unsupported image format")
        image_url = f"data:image/{image.format.lower()};base64," + base64.b64encode(image_bytes).decode('utf-8')
        return image_url
    except (UnidentifiedImageError, ValueError) as e:
        logger.error(f"Error processing image bytes: {e}")
        raise
