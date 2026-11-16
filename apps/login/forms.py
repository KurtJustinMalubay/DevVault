from django.contrib.auth.forms import AuthenticationForm

INPUT_CLASSES = (
    'w-full rounded-lg bg-vault-950/60 border border-white/10 px-4 py-2.5 '
    'text-sm text-ink placeholder:text-mute/60 focus:outline-none '
    'focus:ring-2 focus:ring-brass/60 focus:border-brass/60 transition'
)


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'yourhandle',
            'autocomplete': 'username',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022',
            'autocomplete': 'current-password',
        })
