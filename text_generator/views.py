import logging
from django.http import JsonResponse
from django.shortcuts import render
import google.generativeai as genai
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_text_Llama_2_70b_hf(prompt):
    response = requests.post(settings.API_URL_Llama_2_70b_hf, headers=settings.HEADERS, json={'inputs': prompt})
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError as e:
            logger.error(f"JSON decoding error: {e}")
            return 'Failed to decode response'
    else:
        logger.error(f"API call failed with status code {response.status_code}")
        return 'Failed to generate text'


def generate_text_genie(prompt):
    try:
        genai.configure(api_key=settings.API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        print(response.text)
        return response.text
    except Exception as e:
        logger.error(f"Error generating text with genie: {e}")
        return 'Failed to generate text'


def chat_text(request):
    return render(request, template_name="text_generator/chat_bot.html", context={})


def generate_chat_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prompt = request.POST.get('prompt')
    selected_model = request.POST.get('selectedApi')

    if not prompt or not selected_model:
        return JsonResponse({'error': 'Missing prompt or selected model'}, status=400)

    try:
        if selected_model == 'gemini-pro':
            text_response = generate_text_genie(prompt)
        elif selected_model == 'Llama-2-70b-hf':
            text_response = generate_text_Llama_2_70b_hf(prompt)
        else:
            return JsonResponse({'error': 'Invalid model selected'}, status=400)
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return JsonResponse({'error': 'Failed to generate text'}, status=500)

    return JsonResponse({'text_response': text_response})
