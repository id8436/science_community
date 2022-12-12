from django import forms
from .models import *

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'year', 'level', 'school_code', 'education_office']
class HomeroomForm(forms.ModelForm):
    class Meta:
        model = Homeroom
        fields = ['name']

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['subject']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['subject', 'content']

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['subject', 'content', 'deadline']
