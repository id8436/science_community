from django import forms
from .models import Posting, Answer, Comment, Board, Exam_profile

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['enter_year',]

class PostingForm(forms.ModelForm):
    class Meta:
        model = Posting
        fields = ['subject', 'content', 'source',  # 요건 일반 게시판에서 사용됨.
                  'boolean_1', 'boolean_2',  # 건의에서 사용.
                  ]

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

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Exam_profile
        fields = ['test_code']