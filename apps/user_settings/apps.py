from django.apps import AppConfig


class UserSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_settings'
    label = 'user_settings'

    def ready(self):
        # Every new User automatically gets a matching UserSettings row
        # with sensible defaults.
        from . import signals  # noqa: F401
