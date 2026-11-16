from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Entry, Membership, Workspace


class WorkspaceWithoutMembershipTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='solo',
            password='Vault-password-281!',
        )
        self.client.force_login(self.user)

    def test_entry_creation_returns_home_instead_of_failing_without_workspace(self):
        response = self.client.get(reverse('home:entry-create'))

        self.assertRedirects(response, reverse('home:home'))
        self.assertFalse(Entry.objects.exists())

    def test_invite_returns_home_instead_of_404_without_workspace(self):
        response = self.client.get(reverse('home:workspace-invite'))

        self.assertRedirects(response, reverse('home:home'))


class ExistingFeatureFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='maker',
            password='Vault-password-281!',
        )
        self.client.force_login(self.user)

    def test_workspace_switch_redirects_to_safe_local_next_url(self):
        workspace = Workspace.objects.create(name='Nightfall', owner=self.user)
        Membership.objects.create(
            user=self.user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )
        next_url = '/entries/?q=shader'

        response = self.client.post(
            reverse('home:workspace-switch'),
            {'workspace_id': workspace.pk, 'next': next_url},
        )

        self.assertRedirects(response, next_url)
        self.assertEqual(self.client.session['active_workspace_id'], workspace.pk)

    def test_workspace_switch_rejects_external_next_url(self):
        workspace = Workspace.objects.create(name='Nightfall', owner=self.user)
        Membership.objects.create(
            user=self.user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )

        response = self.client.post(
            reverse('home:workspace-switch'),
            {'workspace_id': workspace.pk, 'next': 'https://attacker.example/path'},
        )

        self.assertRedirects(response, reverse('home:home'))

    def test_owner_invite_respects_five_member_limit(self):
        workspace = Workspace.objects.create(name='Nightfall', owner=self.user)
        Membership.objects.create(
            user=self.user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )
        self.client.get(reverse('home:home'))
        for index in range(3):
            member = get_user_model().objects.create_user(username=f'member{index}')
            Membership.objects.create(user=member, workspace=workspace)
        invitee = get_user_model().objects.create_user(username='lastmember')

        response = self.client.post(
            reverse('home:workspace-invite'),
            {'identifier': invitee.username},
        )
        self.assertRedirects(response, reverse('home:workspace-invite'))
        self.assertEqual(workspace.member_count, 5)

        overflow_user = get_user_model().objects.create_user(username='overflow')
        response = self.client.post(
            reverse('home:workspace-invite'),
            {'identifier': overflow_user.username},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This vault already has five members.')
        self.assertFalse(Membership.objects.filter(workspace=workspace, user=overflow_user).exists())

    def test_workspace_and_entry_create_edit_comment_delete(self):
        response = self.client.post(
            reverse('home:workspace-create'),
            {'name': 'Nightfall'},
        )
        self.assertRedirects(response, reverse('home:home'))
        workspace = Workspace.objects.get(name='Nightfall')
        self.assertTrue(
            Membership.objects.filter(
                user=self.user,
                workspace=workspace,
                role=Membership.Role.OWNER,
            ).exists()
        )

        response = self.client.post(
            reverse('home:entry-create'),
            {
                'entry_type': Entry.EntryType.BUG,
                'title': 'Broken shader',
                'description': 'Fails on load.',
                'status': Entry.Status.OPEN,
                'tags_input': 'shader, vfx',
            },
        )
        entry = Entry.objects.get(title='Broken shader')
        self.assertRedirects(response, reverse('home:entry-detail', args=[entry.pk]))
        self.assertEqual(set(entry.tags.values_list('name', flat=True)), {'shader', 'vfx'})

        response = self.client.post(
            reverse('home:entry-detail', args=[entry.pk]),
            {'body': 'Reproduced on startup.'},
        )
        self.assertRedirects(response, reverse('home:entry-detail', args=[entry.pk]))
        self.assertEqual(Comment.objects.get(entry=entry).body, 'Reproduced on startup.')

        response = self.client.post(
            reverse('home:entry-edit', args=[entry.pk]),
            {
                'entry_type': Entry.EntryType.BUG,
                'title': 'Fixed shader',
                'description': 'Fails on load.',
                'status': Entry.Status.RESOLVED,
                'tags_input': 'shader',
            },
        )
        self.assertRedirects(response, reverse('home:entry-detail', args=[entry.pk]))
        entry.refresh_from_db()
        self.assertEqual(entry.title, 'Fixed shader')
        self.assertEqual(list(entry.tags.values_list('name', flat=True)), ['shader'])

        response = self.client.get(reverse('home:entries'), {'q': 'Fixed', 'status': 'RESOLVED'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['entries']), [entry])

        response = self.client.post(reverse('home:entry-delete', args=[entry.pk]))
        self.assertRedirects(response, reverse('home:entries'))
        self.assertFalse(Entry.objects.filter(pk=entry.pk).exists())

    def test_entry_detail_is_scoped_to_user_workspaces(self):
        other_user = get_user_model().objects.create_user(
            username='other',
            password='Vault-password-281!',
        )
        workspace = Workspace.objects.create(name='Private', owner=other_user)
        Membership.objects.create(
            user=other_user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )
        entry = Entry.objects.create(
            workspace=workspace,
            author=other_user,
            title='Private entry',
        )

        response = self.client.get(reverse('home:entry-detail', args=[entry.pk]))

        self.assertEqual(response.status_code, 404)

    def test_invalid_comment_renders_form_errors_without_creating_comment(self):
        workspace = Workspace.objects.create(name='Nightfall', owner=self.user)
        Membership.objects.create(
            user=self.user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )
        entry = Entry.objects.create(
            workspace=workspace,
            author=self.user,
            title='Broken shader',
        )

        response = self.client.post(
            reverse('home:entry-detail', args=[entry.pk]),
            {'body': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertFalse(Comment.objects.filter(entry=entry).exists())

    def test_entry_rejects_tags_longer_than_the_database_limit(self):
        workspace = Workspace.objects.create(name='Nightfall', owner=self.user)
        Membership.objects.create(
            user=self.user,
            workspace=workspace,
            role=Membership.Role.OWNER,
        )

        response = self.client.post(
            reverse('home:entry-create'),
            {
                'entry_type': Entry.EntryType.ASSET,
                'title': 'Long tag asset',
                'description': '',
                'status': Entry.Status.OPEN,
                'tags_input': 'x' * 41,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Each tag must be 40 characters or fewer.')
        self.assertFalse(Entry.objects.filter(title='Long tag asset').exists())
