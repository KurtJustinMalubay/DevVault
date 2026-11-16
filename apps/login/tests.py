from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='maker',
            password='Vault-password-281!',
        )

    def test_login_accepts_valid_credentials(self):
        response = self.client.post(
            reverse('login:login'),
            {'username': self.user.username, 'password': 'Vault-password-281!'},
        )

        self.assertRedirects(response, reverse('home:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_renders_error_for_invalid_credentials(self):
        response = self.client.post(
            reverse('login:login'),
            {'username': self.user.username, 'password': 'incorrect'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_logout_ends_authenticated_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('login:logout'))

        self.assertRedirects(response, reverse('login:login'))
        self.assertNotIn('_auth_user_id', self.client.session)
