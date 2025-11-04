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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Calculus Study Group'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the purpose and activities of your group'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 50, 'value': 10})
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chapter 5 Review Session'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What will be covered in this session?'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building, Room Number'}),
            'is_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/j/...'})
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chapter 5 Notes'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of the material'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'})
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')

        if not file and not link:
            raise forms.ValidationError('You must provide either a file or a link')

        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    # Include user fields alongside Profile fields
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = Profile
        fields = ['bio', 'major', 'interests']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself'}),
            'major': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your major or focus'}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your interests'}),
        }

    def __init__(self, *args, **kwargs):
        # Accept `user` for initializing and saving user fields
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def save(self, commit=True, user=None):
        # Allow passing user via save as well
        user_obj = user or self.user
        profile = super().save(commit=False)
        if user_obj:
            user_obj.email = self.cleaned_data.get('email', user_obj.email)
            user_obj.first_name = self.cleaned_data.get('first_name', user_obj.first_name)
            user_obj.last_name = self.cleaned_data.get('last_name', user_obj.last_name)
            if commit:
                user_obj.save()
        if commit:
            profile.save()
        return profile