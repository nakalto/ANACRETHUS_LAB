from django import forms
from .models import Repository


class RepositorySettingsForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = [
            'name',
            'description',
            'is_private',
            'secret_scanning_enabled',
        ]
