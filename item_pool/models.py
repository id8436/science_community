#from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name

class Grade(models.Model):
    grade = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.grade

class SchoolProfile(models.Model):  # 연도, 학교, 학번 조합은 유일하게 만들 수 있을까?
    year = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    student_code = models.IntegerField(null=False)  # 잘못가입하는 녀석들이 꼭 있으니.. unique 옵션은 주지 말자;
    profiles_owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='profiles_owner', on_delete=models.CASCADE)  #쌓인 프로필의 주인
    def __str__(self):
        return str(self.year) + str(self.school) + str(self.student_code)

class Question(models.Model):
    author =models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="question_author")  # 사용자가 지워져도 profile이 대체하도록.
    major=models.CharField(max_length=10)  #대분류
    division=models.CharField(max_length=10)  #중분류
    subclass=models.CharField(max_length=10)  #소분류

    subject =models.CharField(max_length=100)  #제목
    content = models.TextField()#내용, 문제내기.

    rightAnswer = models.TextField()  #답 쓰기.(json형식으로 가능한 답을 다 써보도록 하자.)
    solution = models.TextField()  # 해설.
    correct=models.IntegerField(null=True, blank=True, default=0)  # 맞은 사람 카운트.
    wrong=models.IntegerField(null=True, blank=True, default=0)  # 틀린 사람 카운트.

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    
    favorite = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="question_favorite") # 즐겨찾는 문제 지정하기 위함

    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='question_like_users')
    like_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    dislike_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='question_dislike_users')
    dislike_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    interest_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='question_interest_users')
    interest_count = models.IntegerField(default=0)

    def __str__(self):
        return self.subject

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="question_answer_author")
    content = models.CharField(max_length=300)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="question_answer_voter")

class Comment(models.Model):
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='question_comment_author')
    content = models.CharField(max_length=300)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="question_comment_voter")



'''

'''