# Import necessary modules

import io
import base64
import requests
import logging
from urllib.parse import quote_plus
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def search_images_pexels(prompt):
    query = quote_plus(prompt.lower())
    PEXELS_API_URL = f'https://api.pexels.com/v1/search?query={query}&per_page=1'
    headers = {'Authorization': settings.PEXELS_API_KEY}
    response = requests.get(PEXELS_API_URL, headers=headers)
    data = response.json()
    if 'photos' in data and data['photos']:
        return data['photos'][0]['src']['medium'], data['photos'][0]['url']
    return None


def search_images_stableDiffusion(payload):
    response = requests.post(settings.API_URL_STABLE_DIFFUSION, headers=settings.HEADERS, json=payload)
    return response.content


def search_images_openJourney(payload):
    response = requests.post(settings.API_URL_OPEN_JOURNEY, headers=settings.HEADERS, json=payload)
    return response.content


def search_images_waifuDiffusion(payload):
    response = requests.post(settings.API_URL_OPEN_JOURNEY, headers=settings.HEADERS, json=payload)
    return response.content


def process_image_bytes(image_bytes):
    try:
        image_io = io.BytesIO(image_bytes)
        Image.open(image_io)
        image_url = f"data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8')
        return image_url
    except Exception as e:
        logger.error(f"Error processing image bytes: {e}")
        raise


# View function to render the chat interface
def chat_image(request):
    return render(request, 'image_generator/chat_bot.html')


def generate_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'})

    prompt = request.POST.get('prompt')
    selected_model = request.POST.get('selectedApi')

    if not prompt or not selected_model:
        return JsonResponse({'error': 'Missing prompt or selected model'})

    try:
        if selected_model == 'pexels':
            image_url = search_images_pexels(prompt)
        elif selected_model == 'stableDiffusion':
            image_url = process_image_bytes(search_images_stableDiffusion({'inputs': prompt}))
        elif selected_model == 'openJourney':
            image_url = process_image_bytes(search_images_openJourney({'inputs': prompt}))
        elif selected_model == 'waifuDiffusion':
            image_url = process_image_bytes(search_images_waifuDiffusion({'inputs': prompt}))
        else:
            return JsonResponse({'error': 'Invalid model selected'})
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return JsonResponse({'error': 'Failed to generate image'})

    return JsonResponse({'image_url': image_url})
