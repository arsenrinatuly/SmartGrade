from django import forms
from academics.models import Lesson, Subject, ClassRoom
from accounts.models import User

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['subject', 'classroom', 'teacher', 'date', 'topic']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'classroom': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='TEACHER')
