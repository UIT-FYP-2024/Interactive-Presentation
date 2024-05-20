import logging
import google.generativeai as genai
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def generate_text_open_llm_leaderboard(payload):
    url = settings.API_URL_OPEN_LLM_LEADERBOARD
    response = requests.post(url, json={"data": [payload]})
    return response.json()["data"][0]


def generate_text_genie(payload):
    genai.configure(api_key=settings.API_KEY_GEMINI)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(payload)
    return response.text


def chat_text(request):
    return render(request, template_name="text_generator/chat_bot.html", context={})


def generate_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prompt = request.POST.get('prompt')
    selected_model = request.POST.get('selectedApi')

    if not prompt or not selected_model:
        return JsonResponse({'error': 'Missing prompt or selected model'}, status=400)

    try:
        if selected_model == 'gemini-pro':
            text_response = generate_text_genie(prompt)
        elif selected_model == 'open_llm_leaderboard':
            text_response = generate_text_open_llm_leaderboard(prompt)
        else:
            return JsonResponse({'error': 'Invalid model selected'}, status=400)
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return JsonResponse({'error': 'Failed to generate text'}, status=500)

    return JsonResponse({'text_response': text_response})
