import io
import base64
import logging
import requests
from urllib.parse import quote_plus
from PIL import Image, UnidentifiedImageError
from django.conf import settings

logger = logging.getLogger(__name__)


def search_images_pexels(prompt: str) -> tuple[str, str] | None:
    """
    Search for images on Pexels using the given prompt.

    Args:
        prompt (str): The search query.

    Returns:
        tuple[str, str] | None: The URL of the medium-sized image and the source URL, or None if no image is found.
    """
    query = quote_plus(prompt.lower())
    url = f'{settings.PEXELS_API_URL}?query={query}&per_page=1'
    headers = {'Authorization': settings.PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'photos' in data and data['photos']:
            return data['photos'][0]['src']['medium'], data['photos'][0]['url']
    except requests.RequestException as e:
        logger.error(f"Error fetching image from Pexels: {e}")
    return None


def make_image_request(url: str, payload: dict) -> bytes:
    """
    Make a POST request to the given URL with the provided payload.

    Args:
        url (str): The URL to make the request to.
        payload (dict): The JSON payload for the request.

    Returns:
        bytes: The response content as bytes.
    """
    try:
        response = requests.post(url, headers=settings.HEADERS, json=payload)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.error(f"Error fetching image from {url}: {e}")
        raise


def search_images_stable_diffusion(payload: dict) -> bytes:
    """
    Search for images using the Stable Diffusion API.

    Args:
        payload (dict): The JSON payload for the request.

    Returns:
        bytes: The response content as bytes.
    """
    return make_image_request(settings.STABLE_DIFFUSION_URL, payload)


def search_images_open_journey(payload: dict) -> bytes:
    """
    Search for images using the Open Journey API.

    Args:
        payload (dict): The JSON payload for the request.

    Returns:
        bytes: The response content as bytes.
    """
    return make_image_request(settings.OPEN_JOURNEY_URL, payload)


def search_images_waifu_diffusion(payload: dict) -> bytes:
    """
    Search for images using the Waifu Diffusion API.

    Args:
        payload (dict): The JSON payload for the request.

    Returns:
        bytes: The response content as bytes.
    """
    return make_image_request(settings.WAIFU_DIFFUSION_URL, payload)


def process_image_bytes(image_bytes: bytes) -> str:
    """
    Process the given image bytes and return a base64-encoded data URL.

    Args:
        image_bytes (bytes): The image bytes to process.

    Returns:
        str: The base64-encoded data URL of the image.
    """
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
