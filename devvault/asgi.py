"""ASGI config for the DevVault project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devvault.settings')

application = get_asgi_application()
