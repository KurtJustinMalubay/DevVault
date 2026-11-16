from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserSettingsFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='maker',
            password='Vault-password-281!',
        )
        self.client.force_login(self.user)

    def test_settings_page_renders_and_persists_preferences(self):
        response = self.client.get(reverse('user_settings:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reduce motion')

        response = self.client.post(
            reverse('user_settings:settings'),
            {
                'email_notifications': 'on',
                'compact_dashboard': 'on',
                'reduced_motion': 'on',
                'show_timestamps': 'on',
            },
        )

        self.assertRedirects(response, reverse('user_settings:settings'))
        self.user.settings.refresh_from_db()
        self.assertFalse(self.user.settings.dark_mode)
        self.assertTrue(self.user.settings.email_notifications)
        self.assertTrue(self.user.settings.compact_dashboard)
        self.assertTrue(self.user.settings.reduced_motion)
        self.assertTrue(self.user.settings.show_timestamps)

        response = self.client.get(reverse('user_settings:settings'))
        self.assertIn(b'<html lang="en" class="reduced-motion">', response.content)
        self.assertIn(b'theme-light', response.content)
        self.assertIn(b'compact', response.content)

    def test_unchecked_preferences_are_saved_as_false(self):
        self.client.post(reverse('user_settings:settings'), {})

        self.user.settings.refresh_from_db()
        self.assertFalse(self.user.settings.dark_mode)
        self.assertFalse(self.user.settings.email_notifications)
        self.assertFalse(self.user.settings.compact_dashboard)
        self.assertFalse(self.user.settings.reduced_motion)
        self.assertFalse(self.user.settings.show_timestamps)
