from django import forms

from .models import Profile

INPUT_CLASSES = (
    'w-full rounded-lg bg-vault-950/60 border border-white/10 px-4 py-2.5 '
    'text-sm text-ink placeholder:text-mute/60 focus:outline-none '
    'focus:ring-2 focus:ring-brass/60 focus:border-brass/60 transition'
)


class ProfileForm(forms.ModelForm):
    """Screen: Profile. Lets a user edit their own Profile feature data."""

    avatar_color = forms.RegexField(
        regex=r'^#[0-9a-fA-F]{6}$',
        error_messages={'invalid': 'Enter a valid color.'},
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES + ' font-mono',
            'type': 'color',
        }),
    )

    class Meta:
        model = Profile
        fields = ('display_name', 'bio', 'avatar_color', 'avatar_image')
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g. Wilmark',
            }),
            'bio': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 3,
                'placeholder': 'Tell your team a bit about yourself…',
            }),
            'avatar_image': forms.ClearableFileInput(attrs={
                'class': 'text-sm text-mute file:mr-3 file:rounded-md file:border-0 '
                         'file:bg-brass/10 file:px-3 file:py-2 file:text-brass '
                         'hover:file:bg-brass/20',
            }),
        }
