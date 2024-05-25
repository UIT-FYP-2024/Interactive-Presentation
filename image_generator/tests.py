import unittest
from io import BytesIO
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from .utils import *


class ChatImageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_image_view(self):
        response = self.client.get(reverse('chat_image'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'image_generator/chat_bot.html')


class GenerateChatImageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('generate_chat')

    def test_generate_chat_image_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Invalid request method'})

    def test_generate_chat_image_missing_prompt(self):
        response = self.client.post(self.url, {'selectedApi': 'pexels'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Missing prompt or selected model'})

    def test_generate_chat_image_missing_model(self):
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Missing prompt or selected model'})

    def test_generate_chat_image_invalid_model(self):
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'invalidModel'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Invalid model selected'})

    @patch('image_generator.views.search_images_pexels')
    def test_generate_chat_image_pexels_success(self, mock_search_images_pexels):
        mock_search_images_pexels.return_value = 'https://example.com/image.jpg'
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'pexels'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'image_url': 'https://example.com/image.jpg'})

    @patch('image_generator.views.search_images_stableDiffusion')
    @patch('image_generator.views.process_image_bytes')
    def test_generate_chat_image_stableDiffusion_success(self, mock_process_image_bytes,
                                                         mock_search_images_stableDiffusion):
        mock_search_images_stableDiffusion.return_value = b'image_bytes'
        mock_process_image_bytes.return_value = 'https://example.com/image.jpg'
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'stableDiffusion'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'image_url': 'https://example.com/image.jpg'})

    @patch('image_generator.views.search_images_openJourney')
    @patch('image_generator.views.process_image_bytes')
    def test_generate_chat_image_openJourney_success(self, mock_process_image_bytes, mock_search_images_openJourney):
        mock_search_images_openJourney.return_value = b'image_bytes'
        mock_process_image_bytes.return_value = 'https://example.com/image.jpg'
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'openJourney'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'image_url': 'https://example.com/image.jpg'})

    @patch('image_generator.views.search_images_waifuDiffusion')
    @patch('image_generator.views.process_image_bytes')
    def test_generate_chat_image_waifuDiffusion_success(self, mock_process_image_bytes,
                                                        mock_search_images_waifuDiffusion):
        mock_search_images_waifuDiffusion.return_value = b'image_bytes'
        mock_process_image_bytes.return_value = 'https://example.com/image.jpg'
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'waifuDiffusion'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'image_url': 'https://example.com/image.jpg'})

    @patch('image_generator.views.search_images_pexels')
    def test_generate_chat_image_error(self, mock_search_images_pexels):
        mock_search_images_pexels.side_effect = Exception('Error')
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'pexels'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Failed to generate image'})


class UtilsTestCase(unittest.TestCase):
    @patch('requests.get')
    def test_search_images_pexels_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'photos': [
                {
                    'src': {'medium': 'https://example.com/image.jpg'},
                    'url': 'https://example.com/image_page'
                }
            ]
        }
        mock_get.return_value = mock_response

        prompt = 'A beautiful sunrise'
        result = search_images_pexels(prompt)
        self.assertEqual(result, ('https://example.com/image.jpg', 'https://example.com/image_page'))

    @patch('requests.get')
    def test_search_images_pexels_no_photos(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'photos': []}
        mock_get.return_value = mock_response

        prompt = 'A beautiful sunrise'
        result = search_images_pexels(prompt)
        self.assertIsNone(result)

    @patch('requests.post')
    def test_search_images_stableDiffusion_success(self, mock_post):
        mock_response = Mock()
        mock_response.content = b'image_bytes'
        mock_post.return_value = mock_response

        payload = {'inputs': 'A beautiful sunrise'}
        result = search_images_stable_diffusion(payload)
        self.assertEqual(result, b'image_bytes')

    @patch('requests.post')
    def test_search_images_openJourney_success(self, mock_post):
        mock_response = Mock()
        mock_response.content = b'image_bytes'
        mock_post.return_value = mock_response

        payload = {'inputs': 'A beautiful sunrise'}
        result = search_images_open_journey(payload)
        self.assertEqual(result, b'image_bytes')

    @patch('requests.post')
    def test_search_images_waifuDiffusion_success(self, mock_post):
        mock_response = Mock()
        mock_response.content = b'image_bytes'
        mock_post.return_value = mock_response

        payload = {'inputs': 'A beautiful sunrise'}
        result = search_images_waifu_diffusion(payload)
        self.assertEqual(result, b'image_bytes')

    def test_process_image_bytes_success(self):
        image = Image.new('RGB', (100, 100))
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_bytes = image_io.getvalue()

        result = process_image_bytes(image_bytes)
        expected_result = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8')
        self.assertEqual(result, expected_result)

    @patch('logging.Logger.error')
    def test_process_image_bytes_failure(self, mock_logger_error):
        invalid_image_bytes = b'not_an_image'

        with self.assertRaises(Exception):
            process_image_bytes(invalid_image_bytes)
        mock_logger_error.assert_called()


if __name__ == '__main__':
    unittest.main()
