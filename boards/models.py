from django.conf import settings
from django.db import models

class Board(models.Model):
    board_name = models.ForeignKey('Board_name', on_delete=models.PROTECT, null=True, blank=True)  # board_name.
    category = models.ForeignKey('Board_category', on_delete=models.PROTECT, null=True, blank=True)
    enter_year = models.IntegerField()  # 입학년도 혹은 개최년도를 기입하자.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name='board_author')
    text_1 = models.ManyToManyField('Comment', blank=True, related_name='+')  # 한 줄 코멘트 다는 용도. 혹은 컨텐츠.
    text_2 = models.ManyToManyField('Comment', blank=True, related_name='+')

    interest_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='board_interest_users')
    interest_count = models.IntegerField(default=0)
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

    tag = models.ManyToManyField('Tag', blank=True)  # 태그 모델과 연결.
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_like_users')
    like_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    dislike_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_dislike_users')
    dislike_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    interest_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_interest_users')
    interest_count = models.IntegerField(default=0)

    source = models.TextField(null=True, blank=True)  # 출처 표기. + 정답 저장용으로 사용. +
    boolean_1 = models.BooleanField(default=True, null=True, blank=True)  # 저자 공개여부로 사용.(비공개가 False)
    boolean_2 = models.BooleanField(default=True, null=True, blank=True)  # 내용 공개여부로 사용.(비공개가 False)
    boolean_3 = models.BooleanField(default=False, null=True, blank=True)  # 건의사항 해결 여부로 사용(처리하면 True)
    report_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='report_user', on_delete=models.SET_NULL)  # 유저 신고용.
    def __str__(self):
            return str(self.subject)


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