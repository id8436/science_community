from django.db import models
from django.conf import settings

class School(models.Model):
    name = models.CharField(max_length=10)
    year = models.IntegerField()
    level = models.CharField(max_length=10)  # 초중고대, 대학원 + 기타.
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)  # 메인관리자. 마스터는 등록 안했다면 비게끔.
    school_code = models.CharField(max_length=20, null=True, blank=True)  # 나이스 api 이용을 위한 학교코드
    education_office = models.CharField(max_length=20, null=True, blank=True)  # 나이스 api 이용을 위한 교육청코드

    def __str__(self):
        return self.name + str(self.year)
    class Meta:
        unique_together = (
            ('name', 'year')
        )
class Homeroom(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    grade = models.IntegerField(null=True, blank=True)   # 학년
    cl_num = models.IntegerField(null=True, blank=True)  # 반
    name = models.CharField(max_length=20, null=True, blank=True)  # 학년반 대신 학급명을 사용하는 경우.
    master = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, blank=True)  # 메인관리자.
    code = models.TextField()  # 비밀코드
    def __str__(self):
        return self.name
    class Meta:
        unique_together = (
            ('school', 'grade', 'cl_num')
        )
class Classroom(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE)  # 학교 아래 귀속시키기 위함.
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE)  # 학생명단을 가져올 홈룸.
    subject = models.CharField(max_length=10)  # 과목명
    master = models.ForeignKey('Teacher', on_delete=models.PROTECT)  # 메인관리자.
    name = models.CharField(max_length=25)  # 클래스 이름. 과목명으로 대신하면 될듯. 이건 없어도 될듯?
    code = models.TextField()  # 가입을 위한 비밀코드
    def __str__(self):
        return str(self.homeroom) + ' ' + self.subject
    class Meta:
        unique_together = (
            ('school', 'homeroom', 'subject')
        )

class Teacher(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name='teacher_user')  # 교사계정 소유자.
    obtained = models.BooleanField(default=False)
    name = models.CharField(max_length=10)  # 실명을 기입하게 하자.
    code = models.TextField(null=True, blank=True)  # 교사프로필을 습득할 수 있게 하는 코드. 습득 후 지우게끔 하자. 코드가 1이 되면 소유하고 있음.
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now=True, null=True, blank=True)
    # 소유 객체들.
    school = models.ForeignKey('School', on_delete=models.CASCADE)  # 어느 학교 소속 프로필인가.
    # homeroom_have = models.ManyToManyField('Homeroom', blank=True)  # 권한을 가진 홈룸. 그런거 없이, 학교권한으로 접근.
    classroom_have = models.ManyToManyField('Classroom', blank=True)  # 권한을 가진 클래스룸.(공동관리가 필요할 경우)
    # 담임, 과목정보?
    #grade = models.IntegerField(null=True, blank=True)  # 학년. 추후 없애도록 해보자.
    #cl_num = models.IntegerField(null=True, blank=True)  # 반. 추후 없애도록 해보자.
    def __str__(self):
        return self.name
    class Meta:
        unique_together = (
            ('school', 'name')
        )


class Student(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='student_user')
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    homeroom = models.ManyToManyField('Homeroom')
    #number = models.IntegerField()  # 학생번호. 지우자.
    student_code = models.CharField(max_length=20, null=True, blank=True)  # 학생 인증코드.(학번 등)
    name = models.CharField(max_length=10)  # 학생 이름.
    obtained = models.BooleanField(default=False)
    code = models.TextField(null=True, blank=True)
    activated = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.school) + " " + str(self.student_code)+ self.name
    class Meta:
        unique_together = (
            ('school', 'student_code')
        )
        ordering = ['student_code']
class Announcement(models.Model):
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 학급.
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 교실.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="Announce_author")
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return self.subject
class AnnoIndividual(models.Model):
    '''개별적으로 전달되는 공지.'''
    base_announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE)
    to_student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 각 개별 학생에게 전달되게끔.
    content = models.TextField(default=None, null=True, blank=True)  # 공지 내용.
    check = models.BooleanField(default=False)  # 확인 했는지 여부.
    check_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.to_student.name

# 아래는 천천히 구현해보자. 과제제출.
class Homework(models.Model):
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 학급.
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 교실.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="Homework_author")
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.subject
class HomeworkSubmit(models.Model):
    '''과제제출.'''
    base_homework = models.ForeignKey('Homework', on_delete=models.CASCADE)
    to_student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 각 개별 학생에게 전달되게끔.
    content = models.TextField(default=None, null=True, blank=True)  # 제출한 과제의 내용.
    check = models.BooleanField(default=False)  # 과제 했는지 여부.
    read = models.BooleanField(default=False)  # 과제 열람했는지 여부.
    submit_date = models.DateTimeField(auto_now=True, null=True, blank=True)  # 과제 제출시간.
    def __str__(self):
        return self.to_student.name