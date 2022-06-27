from django.conf import settings
from django.db import models

class Board(models.Model):
    related_name = 'board_'
    board_name = models.ForeignKey('Board_name', on_delete=models.PROTECT, null=True, blank=True)  # board_name.
    category = models.ForeignKey('Board_category', on_delete=models.PROTECT, null=True, blank=True)
    enter_year = models.IntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name=related_name+"author")
    text_1 = models.ManyToManyField('Comment', blank=True, related_name='+')  # 한 줄 코멘트 다는 용도. 혹은 컨텐츠.
    text_2 = models.ManyToManyField('Comment', blank=True, related_name='+')
    def __str__(self):
        return str(self.board_name) + str(self.enter_year)
    class Meta:
        unique_together = (
            ('board_name', 'enter_year')
            )

class Board_name(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Board_category(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Posting(models.Model):
    board = models.ForeignKey('Board', on_delete=models.PROTECT, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name="posting_author")
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용, 문제내기.

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    tag = models.ManyToManyField('Tag')  # 태그 모델과 연결.
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_users')
    like_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    dislike_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dislike_users')
    dislike_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.

    source = models.TextField()  # 출처 표기. + 정답 저장용으로 사용. +
    public = models.BooleanField(default=True)  # 공개여부로 사용.(비공개가 False)
    def __str__(self):
            return self.subject


class Answer(models.Model):  # 세부내용은 필요에 따라..
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name="answer_author")
    content = models.CharField(max_length=300)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="answer_voter")


class Comment(models.Model):
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="comment_voter")

class Tag(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name
'''

'''