from django.contrib import admin

from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'dark_mode',
        'email_notifications',
        'compact_dashboard',
        'reduced_motion',
        'show_timestamps',
    )
    search_fields = ('user__username',)
