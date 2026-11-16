from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profile'
    label = 'profile'

    def ready(self):
        # Import signal handlers so every new User automatically gets a
        # matching Profile row. Registered here (not in models.py) so it
        # only runs once, when Django starts.
        from . import signals  # noqa: F401
