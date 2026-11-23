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
            'default_landing_page',
            'hide_resolved_entries',
            'default_entry_type',
        )
        labels = {
            'default_landing_page': 'Default start page',
            'hide_resolved_entries': 'Hide resolved entries by default',
            'default_entry_type': 'Default type for new entries',
        }
        help_texts = {
            'default_landing_page': 'Choose where you land after signing in.',
            'hide_resolved_entries': 'Resolved entries remain available through the status filter.',
            'default_entry_type': 'Preselect this type when creating a new entry.',
        }
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
            'default_landing_page': forms.Select(attrs={'class': 'settings-select'}),
            'hide_resolved_entries': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-white/20 bg-vault-950 text-brass focus:ring-brass/60',
            }),
            'default_entry_type': forms.Select(attrs={'class': 'settings-select'}),
        }
