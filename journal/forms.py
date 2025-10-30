from django import forms
from academics.models import Lesson, Subject
from .models import GradeRecord, AttendanceRecord


class GradeForm(forms.ModelForm):
    class Meta:
        model = GradeRecord
        fields = ['student', 'subject', 'teacher', 'value', 'max_value', 'date', 'note']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['lesson', 'student', 'status', 'comment']