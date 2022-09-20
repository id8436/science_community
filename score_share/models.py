from django.db import models
from school_report.models import Student, School
from django.conf import settings


class Exam(models.Model):
    name = models.CharField(max_length=30)  # 시험명.
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)  # 주관단체
    year = models.IntegerField()  # 주관단체의 몇년도 모델에 연결할 것인가. get or create로 연결하면 될듯.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  # 게시자.
    test_code_min = models.IntegerField()  # 수험번호의 최소
    test_code_max = models.IntegerField()  # 수험번호의 최대. 생태교란자를 파악하기 위함.
    association = models.ForeignKey('Exam', on_delete=models.SET_NULL, null=True, blank=True)  # 연관실험.(시간연속성)
    def __str__(self):
        return self.name + str(self.year)
    class Meta:
        unique_together = (
            ('name', 'year')
        )
class Subject(models.Model):
    '''시험 하위 과목'''  # form에서 컴마로 구분되게 하면 어떨까? 태그 기입하듯.
    base_exam = models.ForeignKey('Exam', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)  # 과목명.
    class Meta:
        unique_together = (
            ('name', 'base_exam')
        )
class Exam_profile(models.Model):
    '''테스트에서 비공개로 댓글 등을 사용하기 위함. + 점수 보게끔.'''
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name='exam_user')
    name = models.CharField(max_length=10)  # 랜덤한 숫자와 글자 조합으로 구성하게 할까.

class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저에 직접 담자.
    test_code = models.IntegerField()  # 수험번호.
    base_subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    score = models.IntegerField()  # 한 번 기입하면 변경이 불가능. 아니, 이력이 남게 하면 어때?
    real_score = models.IntegerField()

class Answer(models.Model):  # 세부내용은 필요에 따라..
    posting = models.ForeignKey(Exam, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='score_answer_author')
    content = models.CharField(max_length=300)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="score_answer_voter")


class Comment(models.Model):
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='score_comment_author')
    content = models.CharField(max_length=150)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="score_comment_voter")


