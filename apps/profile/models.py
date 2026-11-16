from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    The Profile feature owns everything about "who this user is" beyond
    the bare Django User record: display name, avatar color, bio, and an
    optional profile picture. One Profile per User, created automatically
    the moment a User is created (see signals.py) so every part of the
    app can safely assume request.user.profile exists.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Shown on entries and comments instead of the raw username.",
    )
    bio = models.TextField(
        blank=True,
        help_text="A short line about you or your role on the team.",
    )
    avatar_color = models.CharField(
        max_length=7,
        default='#E3A537',
        help_text="Hex color used for this user's initials badge in the UI.",
    )
    avatar_image = models.ImageField(
        upload_to='profile/',
        blank=True,
        null=True,
        help_text="Optional profile picture. Falls back to the initials badge when empty.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def initials(self):
        name = self.display_name or self.user.username
        parts = [p for p in name.replace('_', ' ').split() if p]
        if not parts:
            return '?'
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
