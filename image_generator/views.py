from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
import logging

logger = logging.getLogger(__name__)

# Constants for model names
MODEL_PEXELS = 'pexels'
MODEL_STABLE_DIFFUSION = 'stableDiffusion'
MODEL_OPEN_JOURNEY = 'openJourney'
MODEL_WAIFU_DIFFUSION = 'waifuDiffusion'


# View function to render the chat interface
def chat_image(request):
    """
    Render the chat interface for image generation.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered chat interface page.
    """
    return render(request, 'image_generator/chat_bot.html')


def generate_chat_image(request):
    """
    Generate an image based on the user's prompt and selected model.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the image URL or an error message.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prompt = request.POST.get('prompt')
    selected_model = request.POST.get('selectedApi')

    if not prompt or not selected_model:
        return JsonResponse({'error': 'Missing prompt or selected model'}, status=400)

    try:
        if selected_model == MODEL_PEXELS:
            result = search_images_pexels(prompt)
            if not result:
                return JsonResponse({'error': 'No image found from Pexels'}, status=404)
            image_url = result[0]
        elif selected_model == MODEL_STABLE_DIFFUSION:
            image_url = process_image_bytes(search_images_stable_diffusion({'inputs': prompt}))
        elif selected_model == MODEL_OPEN_JOURNEY:
            image_url = process_image_bytes(search_images_open_journey({'inputs': prompt}))
        elif selected_model == MODEL_WAIFU_DIFFUSION:
            image_url = process_image_bytes(search_images_waifu_diffusion({'inputs': prompt}))
        else:
            return JsonResponse({'error': 'Invalid model selected'}, status=400)
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to generate image'}, status=500)

    return JsonResponse({'image_url': image_url})
