from django import forms

from .models import UserSettings


class UserSettingsForm(forms.ModelForm):
    """Screen: Settings. Lets a user edit their own preferences."""

    class Meta:
        model = UserSettings
        fields = (
            'dark_mode',
            'email_notifications',
            'compact_dashboard',
            'reduced_motion',
            'show_timestamps',
        )
        widgets = {
            'dark_mode': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
            'compact_dashboard': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
            'reduced_motion': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
            'show_timestamps': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
        }
