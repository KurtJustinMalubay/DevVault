from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    """
    The Settings feature owns application preferences — things that
    change how DevVault behaves for this user, as opposed to Profile,
    which owns who the user presents themselves as.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settings',
    )
    dark_mode = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    compact_dashboard = models.BooleanField(
        default=False,
        help_text="Show a denser layout with smaller spacing on the Home screen.",
    )
    reduced_motion = models.BooleanField(default=False)
    show_timestamps = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Settings for {self.user.username}'
