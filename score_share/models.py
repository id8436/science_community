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
    def __str__(self):
        return self.name + str(self.year)
    class Meta:
        unique_together = (
            ('name', 'year')
        )
class Subject(models.Model):
    '''시험 하위 과목'''
    base_exam = models.ForeignKey('Exam', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)  # 과목명.
    class Meta:
        unique_together = (
            ('name', 'base_exam')
        )

class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_code = models.IntegerField()  # 수험번호.
    base_subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    score = models.IntegerField()  # 한 번 기입하면 변경이 불가능.
    real_score = models.IntegerField()



