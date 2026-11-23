from django import forms

from django.contrib.auth import get_user_model

from .models import Entry, Tag, Workspace


INPUT_CLASSES = (
    'w-full rounded-lg bg-vault-950/60 border border-white/10 px-4 py-2.5 '
    'text-sm text-ink placeholder:text-mute/60 focus:outline-none '
    'focus:ring-2 focus:ring-brass/60 focus:border-brass/60 transition'
)


class EntryForm(forms.ModelForm):
    related_entries = forms.ModelMultipleChoiceField(
        queryset=Entry.objects.none(),
        required=False,
        label='Related entries',
        help_text='Connect this entry to other assets, bugs, notes, or decisions in this vault.',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'related-entry-options'}),
    )
    tags_input = forms.CharField(
        required=False,
        max_length=1000,
        label='Tags',
        help_text='Separate tags with commas.',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'ui, shader, vfx',
        }),
    )

    class Meta:
        model = Entry
        fields = ('entry_type', 'title', 'description', 'status', 'image', 'related_entries')
        widgets = {
            'entry_type': forms.Select(attrs={'class': INPUT_CLASSES}),
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Entry title'}),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 7,
                'placeholder': 'Describe the asset, issue, note, or decision.',
            }),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'image': forms.ClearableFileInput(attrs={'class': 'text-sm text-mute'}),
        }

    def __init__(self, *args, workspace=None, **kwargs):
        super().__init__(*args, **kwargs)
        workspace = workspace or getattr(self.instance, 'workspace', None)
        if workspace is not None:
            self.fields['related_entries'].queryset = Entry.objects.filter(
                workspace=workspace,
            ).exclude(pk=self.instance.pk).order_by('entry_type', 'title')
        if self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                self.instance.tags.values_list('name', flat=True)
            )

    def clean_tags_input(self):
        value = self.cleaned_data['tags_input']
        if any(len(name.strip()) > 40 for name in value.split(',')):
            raise forms.ValidationError('Each tag must be 40 characters or fewer.')
        return value

    def save(self, commit=True):
        entry = super().save(commit=commit)
        if commit:
            names = {
                name.strip().lower()
                for name in self.cleaned_data.get('tags_input', '').split(',')
                if name.strip()
            }
            entry.tags.set([Tag.objects.get_or_create(name=name)[0] for name in sorted(names)])
        return entry


class CommentForm(forms.Form):
    body = forms.CharField(
        label='Comment',
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': INPUT_CLASSES,
            'rows': 4,
            'placeholder': 'Add context for your team...',
        }),
    )


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Studio or project name',
            }),
        }


class WorkspaceInviteForm(forms.Form):
    identifier = forms.CharField(
        max_length=150,
        label='Username or email',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'teammate or teammate@example.com',
        }),
    )

    def clean_identifier(self):
        identifier = self.cleaned_data['identifier'].strip()
        user_model = get_user_model()
        user = user_model.objects.filter(username__iexact=identifier).first()
        if user is None:
            user = user_model.objects.filter(email__iexact=identifier).first()
        if user is None:
            raise forms.ValidationError('No account was found with that username or email.')
        self.cleaned_data['invitee'] = user
        return identifier
