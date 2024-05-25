import unittest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sign_up_url = reverse('sign_up')
        self.sign_in_url = reverse('sign_in')
        self.sign_out_url = reverse('sign_out')
        self.recover_password_url = reverse('recover_password')
        self.reset_password_url = reverse('reset_password')
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        User.objects.create_user(**self.user_data)

    def test_sign_up_view_get(self):
        response = self.client.get(self.sign_up_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_registration_advanced.html')

    def test_sign_up_view_post_success(self):
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'send_test_account_settings': 'on',
            'subscribe_to_newsletter': 'on',
            'accept_terms_of_service': 'on'
        }
        with patch('authentication.views.create_user') as mock_create_user:
            response = self.client.post(self.sign_up_url, data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('sign_in'))
            mock_create_user.assert_called_once()

    def test_sign_up_view_post_failure(self):
        data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': 'invalidemail',
            'password': 'password123'
        }
        response = self.client.post(self.sign_up_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_registration_advanced.html')
        self.assertContains(response, "Error during sign-up")

    def test_sign_in_view_get(self):
        response = self.client.get(self.sign_in_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_advanced.html')

    def test_sign_in_view_post_success(self):
        data = {'username': self.user_data['username'], 'password': self.user_data['password']}
        response = self.client.post(self.sign_in_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_sign_in_view_post_failure(self):
        data = {'username': self.user_data['username'], 'password': 'wrongpassword'}
        response = self.client.post(self.sign_in_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_advanced.html')
        self.assertContains(response, "Invalid credentials")

    def test_sign_out_view(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.sign_out_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login_advanced'))

    @patch('authentication.views.send_mail')
    def test_recover_password_view_post_success(self, mock_send_mail):
        data = {'email': self.user_data['email']}
        response = self.client.post(self.recover_password_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_password_recover.html')
        self.assertContains(response, 'Password recovery email sent successfully.')
        mock_send_mail.assert_called_once()

    @patch('authentication.views.send_mail')
    def test_recover_password_view_post_failure(self, mock_send_mail):
        mock_send_mail.side_effect = Exception("Error")
        data = {'email': self.user_data['email']}
        response = self.client.post(self.recover_password_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_password_recover.html')
        self.assertContains(response, 'Failed to send password recovery email.')

    def test_reset_password_view_get(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_password_reset.html')

    def test_reset_password_view_post_success(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        data = {'new_password': 'newpassword123', 'confirm_password': 'newpassword123'}
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sign_in'))
        self.assertTrue(self.client.login(username=self.user_data['username'], password='newpassword123'))

    def test_reset_password_view_post_failure(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        data = {'new_password': 'newpassword123', 'confirm_password': 'differentpassword'}
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_password_reset.html')
        self.assertContains(response, 'Passwords do not match. Please try again.')


if __name__ == '__main__':
    unittest.main()
