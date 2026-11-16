from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

INPUT_CLASSES = (
    'w-full rounded-lg bg-vault-950/60 border border-white/10 px-4 py-2.5 '
    'text-sm text-ink placeholder:text-mute/60 focus:outline-none '
    'focus:ring-2 focus:ring-brass/60 focus:border-brass/60 transition'
)


class RegisterForm(UserCreationForm):
    """Screen: Register."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'you@studio.com',
            'autocomplete': 'email',
        }),
    )
    display_name = forms.CharField(
        required=False,
        max_length=50,
        help_text='Optional — shown on your entries instead of your username.',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'e.g. Wilmark',
        }),
    )
    workspace_name = forms.CharField(
        required=True,
        max_length=100,
        label='Studio / workspace name',
        help_text='We\u2019ll create this as your first vault.',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'e.g. Nightfall Studios',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'display_name', 'workspace_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'yourhandle',
                'autocomplete': 'username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES, 'placeholder': '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022',
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES, 'placeholder': 'Confirm password',
        })

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email
