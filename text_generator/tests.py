import unittest
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from .views import *


class ChatTextViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_text_view(self):
        response = self.client.get(reverse('chat_text'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'text_generator/chat_bot.html')


class GenerateChatTextTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('generate_chat')

    def test_generate_chat_text_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Invalid request method'})

    def test_generate_chat_text_missing_prompt(self):
        response = self.client.post(self.url, {'selectedApi': 'gemini-pro'})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Missing prompt or selected model'})

    def test_generate_chat_text_missing_model(self):
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise'})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Missing prompt or selected model'})

    def test_generate_chat_text_invalid_model(self):
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'invalidModel'})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid model selected'})

    @patch('text_generator.views.generate_text_genie')
    def test_generate_chat_text_gemini_pro_success(self, mock_generate_text_genie):
        mock_generate_text_genie.return_value = 'Generated text.'
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'gemini-pro'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'text_response': 'Generated text.'})

    @patch('text_generator.views.generate_text_genie')
    def test_generate_chat_text_gemini_pro_error(self, mock_generate_text_genie):
        mock_generate_text_genie.side_effect = Exception('Error generating text.')
        response = self.client.post(self.url, {'prompt': 'A beautiful sunrise', 'selectedApi': 'gemini-pro'})
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {'error': 'Failed to generate text'})


class UtilsTestCase(unittest.TestCase):
    @patch('text_generator.views.genai.configure')
    @patch('text_generator.views.genai.GenerativeModel')
    def test_generate_text_genie_success(self, mock_generative_model):
        mock_response = Mock()
        mock_response.text = 'Generated text.'
        mock_model_instance = mock_generative_model.return_value
        mock_model_instance.generate_content.return_value = mock_response

        result = generate_text_genie('A beautiful sunrise')
        self.assertEqual(result, 'Generated text.')

    @patch('text_generator.views.genai.configure')
    @patch('text_generator.views.genai.GenerativeModel')
    def test_generate_text_genie_error(self, mock_configure):
        mock_configure.side_effect = Exception('Error configuring genie.')
        result = generate_text_genie('A beautiful sunrise')
        self.assertEqual(result, 'Failed to generate text')


if __name__ == '__main__':
    unittest.main()
