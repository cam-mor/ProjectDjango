from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, StudyGroup, StudySession, StudyMaterial

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    major = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create user profile
            Profile.objects.create(
                user=user,
                major=self.cleaned_data.get('major', ''),
                bio=self.cleaned_data.get('bio', '')
            )
        return user

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description', 'subject', 'max_members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'max_members': forms.NumberInput(attrs={'min': 2, 'max': 50})
        }
        help_texts = {
            'name': 'Choose a descriptive name for your study group',
            'description': 'Describe the goals and activities of your group',
            'max_members': 'Maximum number of members (2-50)',
        }

class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['title', 'description', 'date', 'start_time', 'end_time', 
                 'location', 'is_online', 'meeting_link']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_online = cleaned_data.get('is_online')
        meeting_link = cleaned_data.get('meeting_link')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('End time must be after start time')

        if is_online and not meeting_link:
            raise forms.ValidationError('Meeting link is required for online sessions')

        return cleaned_data

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'file', 'link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')

        if not file and not link:
            raise forms.ValidationError('You must provide either a file or a link')