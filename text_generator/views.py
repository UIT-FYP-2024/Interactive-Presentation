from django.http import JsonResponse
from django.shortcuts import render
from .utils import generate_text_genie
import logging

logger = logging.getLogger(__name__)

# Constants for model names
MODEL_GEMINI_PRO = 'gemini-pro'


def chat_text(request):
    """
    Render the chat interface for text generation.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered chat interface page.
    """
    return render(request, template_name="text_generator/chat_bot.html", context={})


def generate_chat_text(request):
    """
    Generate text based on the user's prompt and selected model.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the generated text or an error message.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prompt = request.POST.get('prompt')
    selected_model = request.POST.get('selectedApi')

    if not prompt or not selected_model:
        return JsonResponse({'error': 'Missing prompt or selected model'}, status=400)

    try:
        if selected_model == MODEL_GEMINI_PRO:
            text_response = generate_text_genie(prompt)
        else:
            return JsonResponse({'error': 'Invalid model selected'}, status=400)
    except Exception as e:
        logger.error(f"Error generating text: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to generate text'}, status=500)

    return JsonResponse({'text_response': text_response})
