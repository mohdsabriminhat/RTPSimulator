from django import forms
from .models import AdminNote, RequestCert, Feedback

class AdminNoteForm(forms.ModelForm):
    class Meta:
        model = AdminNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'placeholder': 'Enter your note here...', 'rows': 4, 'cols': 50}),
        }

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class RequestCertForm(forms.ModelForm):
    class Meta:
        model = RequestCert
        fields = ['instructor', 'student_name', 'university_name', 'date_completed']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Enter your feedback here...',
                'rows': 4,
                'cols': 50
            }),
        }