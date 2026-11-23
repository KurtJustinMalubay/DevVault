from django.conf import settings
from django.db import models
from django.urls import reverse


class Workspace(models.Model):
    """
    A shared vault for one game-dev team. Kept intentionally small
    (see Membership) — DevVault targets teams of up to 5 people.
    """
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='workspaces',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class Membership(models.Model):
    """Join table between User and Workspace, carrying a role."""

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        MEMBER = 'MEMBER', 'Member'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workspace')

    def __str__(self):
        return f'{self.user} @ {self.workspace} ({self.role})'


class Tag(models.Model):
    """Free-form label used to filter Entries (e.g. 'shader', 'ui', 'vfx')."""
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Entry(models.Model):
    """
    The core unit of DevVault: a tagged, searchable note about an asset,
    bug, general note, or team decision.
    """

    class EntryType(models.TextChoices):
        ASSET = 'ASSET', 'Asset'
        BUG = 'BUG', 'Bug'
        NOTE = 'NOTE', 'Note'
        DECISION = 'DECISION', 'Decision'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='entries')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entries',
    )
    entry_type = models.CharField(max_length=10, choices=EntryType.choices, default=EntryType.NOTE)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')
    image = models.ImageField(upload_to='entries/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'entries'

    def __str__(self):
        return f'[{self.entry_type}] {self.title}'

    def get_absolute_url(self):
        return reverse('home:entry-detail', kwargs={'pk': self.pk})

    @property
    def progress_percent(self):
        if self.status == self.Status.RESOLVED:
            return 100
        if self.status == self.Status.IN_PROGRESS:
            return 50
        return 0

    @property
    def is_open_bug(self):
        return self.entry_type == self.EntryType.BUG and self.status != self.Status.RESOLVED


class Comment(models.Model):
    """A threaded reply on an Entry."""
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.entry}'
