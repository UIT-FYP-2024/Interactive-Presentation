import unittest
from unittest.mock import patch, MagicMock
from django.urls import reverse, resolve
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, SimpleTestCase
from . import views, utils


User = get_user_model()


class UtilsTestCase(TestCase):
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_content_success(self, mock_generative_model, mock_configure):
        mock_response = MagicMock()
        mock_response.text = 'Generated content'
        mock_model_instance = mock_generative_model.return_value
        mock_model_instance.generate_content.return_value = mock_response

        payload = '{"key": "value"}'
        result = utils.generate_content(payload)

        mock_configure.assert_called_once_with(api_key=settings.API_KEY_GEMINI)
        mock_generative_model.assert_called_once_with('gemini-pro')
        mock_model_instance.generate_content.assert_called_once_with(payload)
        self.assertEqual(result, 'Generated content')

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_content_failure(self, mock_generative_model, mock_configure):
        mock_model_instance = mock_generative_model.return_value
        mock_model_instance.generate_content.side_effect = Exception('Error')

        payload = '{"key": "value"}'
        result = utils.generate_content(payload)

        mock_configure.assert_called_once_with(api_key=settings.API_KEY_GEMINI)
        mock_generative_model.assert_called_once_with('gemini-pro')
        mock_model_instance.generate_content.assert_called_once_with(payload)
        self.assertEqual(result, 'Failed to generate content')

    @patch('requests.get')
    def test_search_images_pexels_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'photos': [{'src': {'medium': 'image.jpg'}, 'url': 'image_url'}]}
        mock_get.return_value = mock_response

        image_url, source_url = utils.search_images_pexels('landscape')

        self.assertEqual(image_url, 'image.jpg')
        self.assertEqual(source_url, 'image_url')
        mock_get.assert_called_once_with(
            f'https://api.pexels.com/v1/search?landscape&per_page=1',
            headers={'Authorization': settings.PEXELS_API_KEY}
        )

    @patch('requests.get')
    def test_search_images_pexels_no_photos(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'photos': []}
        mock_get.return_value = mock_response

        result = utils.search_images_pexels('landscape')

        self.assertIsNone(result)
        mock_get.assert_called_once_with(
            f'https://api.pexels.com/v1/search?landscape&per_page=1',
            headers={'Authorization': settings.PEXELS_API_KEY}
        )

    @patch('os.makedirs')
    @patch('os.path.join')
    @patch('os.path.exists')
    @patch('pptx.Presentation')
    def test_create_ppt_success(self, mock_presentation, mock_exists, mock_makedirs):
        mock_exists.return_value = True
        mock_slide_layout = MagicMock()
        mock_slide_layout.configure_mock(name='slide_layout')
        mock_presentation.return_value.slide_layouts.__getitem__.return_value = mock_slide_layout
        mock_slide = MagicMock()
        MagicMock()
        mock_presentation.return_value.slides.add_slide.side_effect = [mock_slide, mock_slide]
        mock_placeholder = MagicMock()
        mock_slide.placeholders = [mock_placeholder, mock_placeholder]

        result = utils.create_ppt('dark_modern', '{"Slide 1": {"title": "Title", "content": "Content"}}',
                                  'Presentation')

        self.assertIsNotNone(result)
        mock_exists.assert_called_once_with('static/stock/templates/dark_modern.pptx')
        mock_presentation.assert_called_once()
        mock_presentation.return_value.slide_layouts.__getitem__.assert_called_once_with(0)
        mock_presentation.return_value.slides.add_slide.assert_called()
        mock_slide.placeholders.__getitem__.assert_called_with(0)
        mock_slide.placeholders.__getitem__.assert_called_with(1)
        mock_makedirs.assert_called_once_with('static/stock/presentations', exist_ok=True)


class PowerPointGeneratorViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_powerpoint_generator_view(self):
        response = self.client.get(reverse('powerpoint_generator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'powerpoint_generator/ppt_generator.html')


class GeneratePresentationViewTest(TestCase):
    @patch('powerpoint_generator.views.extract_form_data')
    @patch('powerpoint_generator.views.generate_prompt')
    @patch('powerpoint_generator.views.create_ppt')
    def test_generate_presentation_success(self, mock_create_ppt, mock_generate_prompt, mock_extract_form_data):
        mock_extract_form_data.return_value = {'topic_name': 'Test', 'template_choice': 'dark_modern',
                                               'no_of_slides': 3}
        mock_generate_prompt.return_value = '{"Slide 1": {"title": "Title", "content": "Content"}}'
        mock_create_ppt.return_value = '/path/to/presentation.pptx'

        response = self.client.post(reverse('generate_presentation'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename="Test.pptx"')
        self.assertEqual(response.get('Content-Type'),
                         'application/vnd.openxmlformats-officedocument.presentationml.presentation')

    @patch('powerpoint_generator.views.extract_form_data')
    def test_generate_presentation_bad_request_missing_fields(self, mock_extract_form_data):
        mock_extract_form_data.return_value = None

        response = self.client.post(reverse('generate_presentation'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'All fields are required and \'No Of Slides\' must be a number.')

    @patch('powerpoint_generator.views.extract_form_data')
    @patch('powerpoint_generator.views.generate_prompt')
    def test_generate_presentation_bad_request_failed_content_generation(self, mock_generate_prompt,
                                                                         mock_extract_form_data):
        mock_extract_form_data.return_value = {'topic_name': 'Test', 'template_choice': 'dark_modern',
                                               'no_of_slides': 3}
        mock_generate_prompt.return_value = None

        response = self.client.post(reverse('generate_presentation'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Failed to generate content for the presentation.')

    @patch('powerpoint_generator.views.extract_form_data')
    @patch('powerpoint_generator.views.generate_prompt')
    @patch('powerpoint_generator.views.create_ppt')
    def test_generate_presentation_bad_request_failed_presentation_creation(self, mock_create_ppt, mock_generate_prompt,
                                                                            mock_extract_form_data):
        mock_extract_form_data.return_value = {'topic_name': 'Test', 'template_choice': 'dark_modern',
                                               'no_of_slides': 3}
        mock_generate_prompt.return_value = '{"Slide 1": {"title": "Title", "content": "Content"}}'
        mock_create_ppt.return_value = None

        response = self.client.post(reverse('generate_presentation'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Failed to create the presentation.')

    @patch('powerpoint_generator.views.extract_form_data')
    @patch('powerpoint_generator.views.generate_prompt')
    @patch('powerpoint_generator.views.create_ppt')
    def test_generate_presentation_bad_request_presentation_file_not_found(self, mock_create_ppt, mock_generate_prompt,
                                                                           mock_extract_form_data):
        mock_extract_form_data.return_value = {'topic_name': 'Test', 'template_choice': 'dark_modern',
                                               'no_of_slides': 3}
        mock_generate_prompt.return_value = '{"Slide 1": {"title": "Title", "content": "Content"}}'
        mock_create_ppt.return_value = '/path/to/non_existing_presentation.pptx'

        response = self.client.post(reverse('generate_presentation'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Presentation file not found.')


class TestUrls(SimpleTestCase):
    def test_powerpoint_generator_url_resolves(self):
        url = reverse('powerpoint_generator')
        self.assertEqual(resolve(url).func, views.powerpoint_generator)

    def test_generate_presentation_url_resolves(self):
        url = reverse('generate_presentation')
        self.assertEqual(resolve(url).func, views.generate_presentation)


if __name__ == '__main__':
    unittest.main()
