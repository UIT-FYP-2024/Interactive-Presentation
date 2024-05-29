from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
import logging

logger = logging.getLogger(__name__)


# View function to render the chat interface
def chat_image_editor(request):
    """
    Render the chat interface for image generation.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered chat interface page.
    """
    return render(request, 'image_editor/chat_bot.html')


def generate_chat_image_editor(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prompt = request.POST.get('prompt')
    image_file = request.FILES.get('image')

    if not prompt or not image_file:
        return JsonResponse({'error': 'Missing prompt or image'}, status=400)

    try:
        image_bytes = image_file.read()
        resized_image_bytes = resize_image(image_bytes)  # Resize image before processing
        processed_image_bytes = remove_background(resized_image_bytes)  # Remove background

        image_url = process_image_bytes(processed_image_bytes)

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to process image'}, status=500)

    return JsonResponse({'image_url': image_url})
