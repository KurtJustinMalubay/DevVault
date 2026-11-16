from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ProfileFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='maker',
            email='maker@example.com',
            password='Vault-password-281!',
        )
        self.client.force_login(self.user)

    def test_profile_page_renders_and_saves_profile_fields(self):
        response = self.client.get(reverse('profile:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

        response = self.client.post(
            reverse('profile:profile'),
            {
                'display_name': 'Studio Maker',
                'bio': 'Builds game assets.',
                'avatar_color': '#336699',
            },
        )

        self.assertRedirects(response, reverse('profile:profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, 'Studio Maker')
        self.assertEqual(self.user.profile.bio, 'Builds game assets.')
        self.assertEqual(self.user.profile.avatar_color, '#336699')

    def test_invalid_profile_color_renders_validation_error(self):
        response = self.client.post(
            reverse('profile:profile'),
            {
                'display_name': 'Studio Maker',
                'bio': '',
                'avatar_color': 'not-a-color',
                'avatar_image': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid color.')
