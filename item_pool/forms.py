from django import forms
from .models import Question,Answer, Comment

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'content','rightAnswer', 'solution']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }

from .models import SchoolProfile
class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields =  ['school', 'grade', 'student_code']
        labels = {
            'student_code': '학번'
        }
