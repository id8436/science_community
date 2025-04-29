from django import forms
from .models import *

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'year', 'level', 'school_code', 'education_office']

class SchoolLostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['where', 'when', 'description', 'photo_item', 'status']

class HomeroomForm(forms.ModelForm):
    class Meta:
        model = Homeroom
        fields = ['name']
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name', 'subject_identifier']
class ClassroomForm(forms.ModelForm):
    '''이 폼은 사용하지 않는다.'''
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
        fields = ['subject', 'content', 'deadline', 'is_secret', 'is_secret_student']
