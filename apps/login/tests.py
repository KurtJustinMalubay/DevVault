from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.user_settings.models import UserSettings


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

    def test_login_uses_entries_as_the_saved_default_landing_page(self):
        self.user.settings.default_landing_page = UserSettings.LandingPage.ENTRIES
        self.user.settings.save(update_fields=['default_landing_page'])

        response = self.client.post(
            reverse('login:login'),
            {'username': self.user.username, 'password': 'Vault-password-281!'},
        )

        self.assertRedirects(response, reverse('home:entries'))

    def test_explicit_next_url_overrides_the_saved_landing_page(self):
        self.user.settings.default_landing_page = UserSettings.LandingPage.ENTRIES
        self.user.settings.save(update_fields=['default_landing_page'])

        response = self.client.post(
            reverse('login:login'),
            {
                'username': self.user.username,
                'password': 'Vault-password-281!',
                'next': '/entries/?type=BUG',
            },
        )

        self.assertEqual(response['Location'], '/entries/?type=BUG')

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
