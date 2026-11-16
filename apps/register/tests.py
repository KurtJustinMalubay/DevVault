from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.home.models import Membership, Workspace
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings


class RegistrationFlowTests(TestCase):
    def test_registration_creates_profile_settings_and_owner_workspace_and_logs_in(self):
        response = self.client.post(
            reverse('register:register'),
            {
                'username': 'newmaker',
                'email': 'newmaker@example.com',
                'display_name': 'New Maker',
                'workspace_name': 'First Vault',
                'password1': 'Vault-password-281!',
                'password2': 'Vault-password-281!',
            },
        )

        self.assertRedirects(response, reverse('home:home'))
        user = get_user_model().objects.get(username='newmaker')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertEqual(user.profile, Profile.objects.get(user=user))
        self.assertEqual(user.profile.display_name, 'New Maker')
        self.assertTrue(UserSettings.objects.filter(user=user).exists())
        workspace = Workspace.objects.get(owner=user, name='First Vault')
        self.assertTrue(
            Membership.objects.filter(
                user=user,
                workspace=workspace,
                role=Membership.Role.OWNER,
            ).exists()
        )
