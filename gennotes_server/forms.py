from django import forms

from .models import EditingApplication


class EditingAppRegistrationForm(forms.ModelForm):

    class Meta:
        model = EditingApplication
        fields = ('name', 'description', 'redirect_uris')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
        }
