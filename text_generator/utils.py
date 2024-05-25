import google.generativeai as genai
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_text_genie(prompt: str) -> str:
    """
    Generate text using the Gemini AI model from Google Generative AI.

    Args:
        prompt (str): The input prompt to generate content from.

    Returns:
        str: The generated text, or an error message if generation fails.
    """
    try:
        genai.configure(api_key=settings.API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating text with genie: {e}", exc_info=True)
        return 'Failed to generate text'
