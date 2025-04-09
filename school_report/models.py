from django.db import models
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import os  # 파일 수정시간 파악을 위해..

'''의견. 훗날 앱 자체를 재구성해보자.
1. 학교, 교실, 교과교실, 교과 등 객체는 하나의 모델로 type 처리해서 활용할 수 있지 않을까? board 모델로 활용해도 괜찮을듯.
2. 댓글모델 같은 건.. 여러 모델에서 끌어다 쓸 수 있으니, 댓글모델에서 상위모델로 지정하지 않고 독립적으로 두는 편이 좋겠다.(좋아요나 이런 것도...)
3. 모델별 하위 함수를 두어, 해당 객체로 이동하는 url 함수를 짜두면... 이런저런 일에 편해지겠지.
4. 관리자가 여럿일 수 있으니, 이에 대한 반영도 할 수 있게 조정되어야 할듯.
5. 학년공지 및 학년 정보를 모아놓아야 할 수도 있으니, 학급 상위로 학년 놓게 하는 것도 괜찮을듯...?
'''

class BaseRoom(models.Model):
    '''기본적인 공간에 대한 것들.'''
    def get_self_type(self):
        '''어느 객체에 속하는지 확인.'''
        if hasattr(self, 'school_code'):  # 속성에 학교코드가 있는 경우.
            return 'school'
        elif hasattr(self, 'cl_num'):
            return 'homeroom'
        elif hasattr(self, 'subject_name'):
            return 'subject'
        elif hasattr(self, 'base_subject'):
            return 'classroom'
    def get_self_url(self):
        '''본인의 경로 얻기'''
        name = f'school_report:{self.get_self_type()}_main'
        return reverse(name, kwargs={'room_id': self.pk})
    class Meta:
        abstract = True  # 이 클래스가 추상 기반 클래스임을 Django에 알립니다.

class School(BaseRoom):
    name = models.CharField(max_length=30, blank=False)
    year = models.IntegerField(blank=False)
    level = models.CharField(max_length=10, blank=False)  # 초중고대, 대학원 + 기타.
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)  # 메인관리자. 마스터는 등록 안했다면 비게끔.
    school_code = models.CharField(max_length=20, null=True, blank=True)  # 나이스 api 이용을 위한 학교코드
    education_office = models.CharField(max_length=20, null=True, blank=True)  # 나이스 api 이용을 위한 교육청코드

    # 각종 정보
    teacher_board_id = models.IntegerField(default=6)  # 학교게시판으로 연결.

    #site_account = models.ManyToManyField('Memo') 버린 모델.
    def __str__(self):
        return self.name + str(self.year)
    class Meta:
        unique_together = (
            ('name', 'year')
        )
class Homeroom(BaseRoom):
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    grade = models.IntegerField(null=True, blank=True)   # 학년
    cl_num = models.IntegerField(null=True, blank=True)  # 반
    name = models.CharField(max_length=20, null=True, blank=True)  # 학년반 대신 학급명을 사용하는 경우.
    master = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)  # 메인관리자.
    master_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, related_name='homeroom_master')  # 이거 완성되면 위는 지우기.
    code = models.TextField()  # 비밀코드
    def __str__(self):
        return self.name
        # if self.name:
        #     return self.name
        # else:
        #     return str('None')
    class Meta:
        unique_together = (
            ('school', 'name')
        )
    def save(self, *args, **kwargs):
        if self.pk is None:
            # 새로운 객체 생성 시 실행할 로직
            is_new = True
            if not self.name and self.grade and self.cl_num:
                self.name =  f'{self.grade}학년 {self.cl_num}반'
        else:
            # 객체 업데이트 시 실행할 로직
            is_new = False
            pass
        super().save(*args, **kwargs)  # 원래의 save 메서드 호출
        if is_new:
            homework_box, created = HomeworkBox.objects.get_or_create(homeroom=self)
            Announce_box, created = AnnounceBox.objects.get_or_create(homeroom=self)
class Subject(BaseRoom):
    '''학교 하위의, 클래스룸을 만들기 위한 교과.'''
    school = models.ForeignKey('School', on_delete=models.CASCADE)  # 학교 아래 귀속시키기 위함.
    subject_name = models.CharField(max_length=20)  # 과목명
    master = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)  # 메인관리자. 아래로 옮겨진 것 같으면 지워버려~
    master_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True)  # 추후 정리 되면 blank 등 속성도 지우자.
    subject_identifier = models.CharField(max_length=10, null=True, blank=True)  # 학생들에게 보여지지 않는 구분자.(같은 과목으로 여러 학년 들어갈 때)
    def __str__(self):
        return self.subject_name
    class Meta:
        unique_together = (
            ('school', 'subject_name', 'master', 'subject_identifier')
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            # 새로운 객체 생성 시 실행할 로직
            is_new = True
        else:
            # 객체 업데이트 시 실행할 로직
            pass
        super().save(*args, **kwargs)  # 원래의 save 메서드 호출
        if is_new:
            homework_box, created = HomeworkBox.objects.get_or_create(subject=self)
            Announce_box, created = AnnounceBox.objects.get_or_create(subject=self)
class Classroom(BaseRoom):
    school = models.ForeignKey('School', on_delete=models.CASCADE)  # 학교 아래 귀속시키기 위함. # 25년이 지나면 지우자.(다 학교 배정 없이 정리될 거니까.)
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE)  # 학생명단을 가져올 홈룸.
    base_subject = models.ForeignKey('Subject', on_delete=models.CASCADE)  # 연결할 모델.
    subject = models.CharField(max_length=10)  # 과목명  # 상위 과목의 과목명으로 연결될 거니까, 25년이 지나면 지워도 괜찮을듯. 그때 위의 null과 블랭크 조건 없애자.
    master = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)  # 메인관리자.
    master_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)  # 훗날 null을 없애는 날이 오길...!
    # 나중에 메인관리자나 관리집단도 유저모델에 직접 연결시키자.
    name = models.CharField(max_length=25, null=True, blank=True)  # 클래스 이름. 과목명으로 대신하면 될듯. 이건 없어도 될듯? 역시, 25년이 지나면 지워도 괜찮을듯.
    def __str__(self):
        return str(self.homeroom) + ' ' + str(self.base_subject)
    class Meta:
        unique_together = (
            ('school', 'homeroom', 'subject')
        )
    def save(self, *args, **kwargs):
        if self.pk is None:
            # 새로운 객체 생성 시 실행할 로직
            is_new = True
        else:
            # 객체 업데이트 시 실행할 로직
            pass
        super().save(*args, **kwargs)  # 원래의 save 메서드 호출
        if is_new:
            homework_box, created = HomeworkBox.objects.get_or_create(Classroom=self)
            Announce_box, created = AnnounceBox.objects.get_or_create(Classroom=self)

class Teacher(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name='teacher_user')  # 교사계정 소유자.
    obtained = models.BooleanField(default=False)
    name = models.CharField(max_length=10)  # 실명을 기입하게 하자.
    code = models.TextField(null=True, blank=True)  # 교사프로필을 습득할 수 있게 하는 코드. 습득 후 지우게끔 하자.
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
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_user')
    # 어드민이지워질 때 학생계정이 지워지면 누군가 악용할 수 있다 싶어서... null로 둔다.
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    homeroom = models.ManyToManyField('Homeroom')
    #number = models.IntegerField()  # 학생번호. 지우자.
    student_code = models.CharField(max_length=20)  # 학생 인증코드.(학번 등)
    name = models.CharField(max_length=10)  # 학생 이름.
    obtained = models.BooleanField(default=False)
    code = models.TextField(null=True, blank=True)  # 인증용.
    activated = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __str__(self):
        return str(self.student_code)+ self.name
    class Meta:
        unique_together = (
            ('school', 'student_code')
        )
        ordering = ['student_code']
class Profile(models.Model):
    # 교사, 학생 정보를 담는 프로필.
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='school_profile')
    # 어드민이지워질 때 학생계정이 지워지면 누군가 악용할 수 있다 싶어서... null로 둔다.
    obtained = models.BooleanField(default=False)  # 등록 되었는지 여부.
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now=True, null=True, blank=True)
    confirm_code = models.TextField(null=True, blank=True)  # 인증용 코드.
    # 정보
    school = models.ForeignKey('School', on_delete=models.CASCADE)  # 어느 학교 소속 프로필인가.
    position = models.CharField(max_length=10)  # teacher or student or parent
    homeroom = models.ManyToManyField('Homeroom', blank=True)
    name = models.CharField(max_length=10)  # 실명을 기입하게 하자.
    code = models.CharField(max_length=20, null=True, blank=True,)  # 학생 학번, 교사번호 등.
    def __str__(self):
        if self.code:
            return str(self.code)+ self.name
        return self.name
    class Meta:
        unique_together = (
            ('school', 'code')  # 교사와 이름도 같고 코드도 같을 일은 없겠지...
        )
        ordering = ['code']  # 기본적으로 학번순 정렬. 학번이 겹칠 일은 없으니... 보조지표는 필요 없을듯?
class BaseBox(models.Model):
    '''각종 Box의 원본이 되는 클래스. 나머지 박스에선 상속받아 쓴다.'''
    '''학교, 교과, 교실 등으로 연결하기 위해 공통적으로 담는 과제박스.'''
    school = models.OneToOneField('School', on_delete=models.CASCADE, default=None, null=True, blank=True)
    homeroom = models.OneToOneField('Homeroom', on_delete=models.CASCADE, default=None, null=True, blank=True)
    classroom = models.OneToOneField('Classroom', on_delete=models.CASCADE, default=None, null=True, blank=True)
    subject = models.OneToOneField('subject', on_delete=models.CASCADE, default=None, null=True, blank=True)  # 교과.
    def __str__(self):
        type, object = self.get_upper_model()
        return str(object) + 'box'
    def type(self):
        '''어느 객체에 속한 박스인지. 속성, id 반환.'''
        if self.school:
            return 'school', self.school.id
        elif self.homeroom:
            return 'homeroom', self.homeroom.id
        elif self.subject:
            return 'subject', self.subject.id
        elif self.classroom:
            return 'classroom', self.classroom.id  # 인수가 2개임에 유의.
    def get_profiles(self, teacher=None):
        '''각 객체 하위의 모든 프로필을 불러온다.'''
        type, id = self.type()
        if type == 'school':
            if teacher=="teacher":
                profiles = Profile.objects.filter(school=self.school, position='teacher')
            else:
                profiles = Profile.objects.filter(school=self.school, position='student')
        elif type == 'homeroom':
            profiles = self.homeroom.profile_set.all()
        elif type == 'subject':
            classrooms = self.subject.classroom_set.all()
            homerooms = list(set([classroom.homeroom for classroom in classrooms]))
            q_objects  = Q() # 비어있는 Q 객체로 시작. 쿼리오브젝트.
            for homeroom in homerooms:
                q_objects |= Q(homeroom=homeroom)
            profiles = Profile.objects.filter(q_objects).distinct()
        elif type == 'classroom':
            homeroom = self.classroom.homeroom
            profiles = homeroom.profile_set.all()
        return profiles
    def get_profiles_id(self, teacher=None):
        '''각 박스에 속한 인원들의 ID 반환.'''
        type, id = self.type()
        if type == 'school':
            if teacher=="teacher":
                profile_ids = Profile.objects.filter(school=self.school, position='teacher').values_list('id', flat=True)
            else:
                profile_ids = Profile.objects.filter(school=self.school, position='student').values_list('id', flat=True)
        elif type == 'homeroom':
            profile_ids = self.homeroom.profile_set.values_list('id', flat=True)
        elif type == 'subject':
            classrooms = self.subject.classroom_set.all()
            homerooms = [classroom.homeroom for classroom in classrooms]
            q_objects = Q()  # 비어있는 Q 객체로 시작. 쿼리오브젝트.
            for homeroom in homerooms:
                q_objects |= Q(homeroom=homeroom)
            profile_ids = Profile.objects.filter(q_objects).values_list('id', flat=True)
        elif type == 'classroom':
            homeroom = self.classroom.homeroom
            profile_ids = homeroom.profile_set.values_list('id', flat=True)
        return profile_ids
    def get_school_model(self):
        type, id = self.type()
        if type == 'school':
            return self.school
        elif type == 'homeroom':
            return self.homeroom.school
        elif type == 'subject':
            return self.subject.school
        elif type == 'classroom':
            return self.classroom.school
    def get_upper_model(self):
        '''박스가 속한 객체 얻기. 무엇인지와 모델'''
        if self.school:
            return 'school', self.school
        elif self.homeroom:
            return 'homeroom', self.homeroom
        elif self.subject:
            return 'subject', self.subject
        elif self.classroom:
            return 'classroom', self.classroom  # 인수가 2개임에 유의.
    def redirect_to_upper(self):
        '''박스를 소유한 객체로 리다이렉트.'''
        type, object_id = self.type()
        if type == 'school':
            return redirect('school_report:school_main', object_id)
        elif type == 'homeroom':
            return redirect('school_report:homeroom_main', object_id)
        elif type == 'subject':
            return redirect('school_report:subject_main', object_id)
        elif type == 'classroom':
            return redirect('school_report:classroom_main', object_id)
    class Meta:
        abstract = True  # 이 클래스가 추상 기반 클래스임을 Django에 알립니다.
class UnderBox(models.Model):
    def get_self_type(self):
        '''과제인지, 공지인지.'''
        if hasattr(self, 'homework_box'):  # 공지 확인.
            return 'homework'
        elif hasattr(self, 'announce_box'):  # 공지 확인.
            return 'announce'
    def get_self_url(self):
        '''본인의 경로 얻기'''
        if self.get_self_type() == 'homework':
            return reverse('school_report:homework_detail', kwargs={'posting_id': self.pk})
        else:
            return reverse('school_report:announcement_detail', kwargs={'posting_id': self.pk})
    def get_upper_box(self):
        '''해당 과제, 공지가 속한 객체 얻기.'''
        if self.get_self_type() == 'homework':
            return self.homework_box
        else:
            return self.announce_box
    class Meta:
        abstract = True  # 이 클래스가 추상 기반 클래스임을 Django에 알립니다.
class HomeworkBox(BaseBox):
    pass
class Homework(UnderBox):
    # 아래의 school은 곧장 연결되는 것으로.. 없을 수도 있음.
    # school이나 홈룸은 있으면 다 넣게 하면 어떨까?
    homework_box = models.ForeignKey('HomeworkBox', on_delete=models.CASCADE, null=True, blank=True)
    # 위 4개 중 하나의 모델로 연결되어 있음.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="Homework_author", blank=True)
    author_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)  # 익명설문 여부.(교사에게도)
    is_secret_student = models.BooleanField(default=False)  # 아래의 원본. 지우자.
    is_secret_user = models.BooleanField(default=False)  # 아직 구현은 안했지만, 학생 대상 익명설문 여부. 설문 대상에게 익명으로 할 경우.
    is_special = models.CharField(max_length=20, null=True, blank=True, default=None)  # 특수평가 종류 입력.
    is_end = models.BooleanField(default=False)  # pending과도 혼용. deadline으로 처리할 수도 있지만.. 특수한 경우를 위해. False를 진행중으로. api작업에서 작업중임을 표시하기 위해서도.
    is_pending = models.BooleanField(default=False)  # 훗날 AI에 활용. is_end가 True로 바뀔 때 False값을 갖게 하자.

    ### 버려질 대상.
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True)  # 학교단위 설문용.
    subject_object = models.ForeignKey('subject', on_delete=models.CASCADE, null=True, blank=True)  # 교과 지정 설문용.
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE, null=True,
                                 blank=True)  # 공지할 학급.  # 학급이나 학교에서 다대다로 가져가는 게 편할듯.
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 교실.

    def __str__(self):
        return self.subject
    def copy_create(self, homework_box, author_profile):
                    #(self, classroom_list=None, subject_list=None, homeroom_list=None):
        '''특정 모델에서 진행되는 카피. 객체의 ID 목록을 받아와 실행한다.'''
        copied_instance = Homework.objects.create(homework_box=homework_box, author_profile=author_profile,
          # 아래는 복사정보.
            subject=self.subject, content=self.content, deadline=self.deadline, is_special=self.is_special)
        # 이전 코드인데, 뭔가 이상함;;; 학급으로의 복사가 안되어, 새로 짬. 잘 되면 지우자.
        # copied_instance = Homework.objects.create(homework_box=self.homework_box,
        #     author_profile=self.author_profile, subject=self.subject, content=self.content, deadline=self.deadline, is_special=self.is_special)
        # # 학교냐, 교과냐, 교실이냐. 어디에 복사할 것인가.
        # for classroom in classroom_list:
        #     classroom_ob = Classroom.objects.get(id=classroom)  # 교실객체 찾기.
        #     copied_instance.classroom = classroom_ob
        # for subject in subject_list:
        #     subject_ob = Subject.objects.get(id=subject)
        #     copied_instance.subject_object = subject_ob
        # for homeroom in homeroom_list:
        #     homeroom_ob = Homeroom.objects.get(id=homeroom)
        #     copied_instance.homeroom_object = homeroom_ob

        # 과제 하위의 설문 질문 복사 및 homework와 연결.
        homework_questions = self.homeworkquestion_set.all()  # all()을 붙여야 하나?
        for homework_question in homework_questions:
            homework_question.question_copy_create(copied_instance)
        copied_instance.save()  # 변경사항은 마지막에 반영.
        return copied_instance
    def to_homework(self):
        '''자기 자신의 페이지 보여주기.'''
        return redirect('school_report:homework_detail', posting_id=self.id)
class HomeworkSubmit(models.Model):
    '''간단 과제제출, 동료평가 설문나누기용.'''
    base_homework = models.ForeignKey('Homework', on_delete=models.CASCADE)
    # to_user에서 학생이 아직 등록하지 않은 상태라면? 경고를 주기라도 해야 할듯.
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # 생각해 보니, 학생이 아니라, 유저로 해야 해. 교사들 설문 등 필요할 때가 있잖아? 아래 프로파일로 대체.
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    default=None  # 이부분은 성공적으로 작동하게 되면 없어도 될듯.
                                   )  # 프로필에 과제 부여. 프로필 완성되면 위 지우자.

    to_student = models.ForeignKey('Student', default=None, on_delete=models.CASCADE, null=True, blank=True)  # 동료평가용. # 프로필 완성되면 지울 것.
    target_profile = models.ForeignKey('Profile', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='target_homeworks')  # 동료평가용.

    title = models.TextField(default=None, null=True, blank=True)  # 학생들에게 전달될 과제명.(혹시나 나중에 기능확장에 대비) #[지워보자.]
    content = models.TextField(default=None, null=True, blank=True)  # 제출한 과제의 내용. # 동료평가 후 최악의 리뷰자 선정. # ai세특에서 df 저장하는 용도.
    ## check, read 등이 아니라 하나의 status로 바꾸면 어때? 하나로 표현하게.
    state = models.CharField(max_length=20, default=None, null=True, blank=True)  # 다양한 상태를 표현하기 위해.
    check = models.BooleanField(default=False)  # 과제 했는지 여부. 지정하는 것과 별개.
    read = models.BooleanField(default=False)  # 과제 열람했는지 여부.
    submit_date = models.DateTimeField(null=True, blank=True)  # 과제 제출시간.
    ## 지워질 대상.
    # def __str__(self):
    #     return str(self.to_user)
    class Meta:
        unique_together = (
            ('base_homework', 'to_profile', 'target_profile')
        )
        ordering = ['id']
    def copy_create(self, homework_ob):
        copied_instance = HomeworkSubmit.objects.create(base_homework=homework_ob,
            to_user=self.to_user, title=self.title,
            content=self.content)
        return copied_instance
class HomeworkQuestion(models.Model):
    '''과제제출 하위의 설문 하나하나.'''
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE)
    question_title = models.TextField(null=True,blank=True)  # 질문.
    question_type = models.TextField(null=True,blank=True)  # 질문유형. 단답형? 숫자? 등등등
    is_essential = models.BooleanField(default=False)  # 필수로 답해야 하는지 여부.
    # 순번 및 특수기능.
    ordering = models.IntegerField(null=True, blank=True)  # 질문의 순번.
    is_special = models.BooleanField(default=False)  # 특수 설문으로, 조정 불가능한 문항임을 알리기 위해.
    # 기능.
    options = models.TextField(null=True, blank=True)  # 문항정보 담기.
    upper_lim = models.FloatField(default=None, null=True, blank=True)  # 숫자 등에 사용하는 상위 리밋.(최대 글자수,체크박스선택갯수,)
    lower_lim = models.FloatField(default=None, null=True, blank=True)  # 숫자 등에 사용하는 하위 리밋.(최소 글자수,체크박스선택갯수,)
    def question_copy_create(self, homework_ob):
        copied_instance = HomeworkQuestion.objects.create(homework=homework_ob,
            question_title=self.question_title, question_type=self.question_type, is_essential=self.is_essential,
            ordering=self.ordering, is_special=self.is_special, options=self.options,
            upper_lim=self.upper_lim, lower_lim=self.lower_lim)
        return copied_instance
    def __str__(self):
        return self.question_title

from datetime import datetime  # 저장경로 관련.
from os.path import basename  # 파일명 관련.

def get_upload_to(instance, filename):
    return 'homework/submit/{}/{}/{}/{}'.format(datetime.now().year, datetime.now().month, datetime.now().day,
                                                filename)
from django.db.models.signals import pre_delete
from django.dispatch import receiver
class HomeworkAnswer(models.Model):
    '''질문의 하위로 구성되어 있음.'''
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  # 응답자. 지워가야 할까? 아니면 임의 설문을 위해 남겨야 하나.
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='homework_answer_user',
                                   default=None  # 이부분은 성공적으로 작동하게 되면 없어도 될듯. submit에 엮이니까. 어차피.
                                   )  # 프로필에 과제 부여. 프로필 완성되면 위 지우자.
    submit = models.ForeignKey('HomeworkSubmit', on_delete=models.CASCADE, blank=True, null=True)  # 동료평가에서 쓰일 평가대상 나누기용 제출.
    to_student = models.ForeignKey('Student', default=None, on_delete=models.CASCADE, null=True, blank=True)  # 동료평가용. 평가 대상자에 대한 정보를 빠르게 모으기 위해.
    target_profile = models.ForeignKey('Profile', default=None, on_delete=models.CASCADE, null=True, blank=True)  # 동료평가용. 정리되면 위 지우자.
    question = models.ForeignKey('HomeworkQuestion', on_delete=models.CASCADE)
    contents = models.TextField(default=None, blank=True, null=True)  # 응답, 선택값들 담기.
    file = models.FileField(upload_to=get_upload_to, default=None, blank=True, null=True)  # 각종 파일을 담기 위한 필드.
    # 자동저장, 임시저장 관련.
    auto_contents = models.TextField(default=None, blank=True, null=True)  # 응답, 선택값들 담기.
    auto_file = models.FileField(upload_to=get_upload_to, default=None, blank=True, null=True)  # 각종 파일을 담기 위한 필드.
    memo = models.TextField(default=None, blank=True, null=True)  # 동료평가에선 (평균-자기점수)**2이 담김.
    def __str__(self):
        return str(self.to_profile) + str(self.target_profile) + str(self.id)
    def save(self, *args, **kwargs):
        '''업로드 파일이 기존 파일과 다를 경우에 기존파일을 삭제하기 위한 save 오버라이드.'''
        # 새 임시저장파일을 올릴 때. 그냥 저장하면 됨.(과거의 것 지우고.)
        if self.auto_file and self.pk:  # 새로 저장하는 객체에선 pk가 주어져 있지 않다.
            previous = HomeworkAnswer.objects.get(id=self.id)  # 기존 저장되어 있는 객체.
            # 만약 기존에 제출한 파일이 있다면...? 기존 파일은 지켜줘야지...!
            if previous.auto_file:  # 기존 자동저장 파일이 있는 경우에만 진행.
                previous_file_path = previous.file.path
                previous_auto_file_path = previous.auto_file.path
                previous_file_time = os.path.getmtime(previous_file_path)
                previous_auto_file_time = os.path.getmtime(previous_auto_file_path)
                if previous_file_time == previous_auto_file_time:  # 기존 임시저장과 기존 제출내용이 같다면..
                    pass  # 파일 삭제 없이 저장하게끔 건너기.
                else:
                    # 다르다면 기존 임시저장 파일 지우고 진행.
                    previous.auto_file.delete(save=False)

        # 새 파일을 제출할 때.(임시저장을 먼저 진행하게끔 되어 있음.)
        if self.file:  # 임시저장을 먼저 하기에, 기존 객체가 있음. 그냥 새 파일의 경로를 임시저장의 것으로 지정하면 될듯.
            previous = HomeworkAnswer.objects.get(id=self.id)  # 기존 저장되어 있는 객체.
            if previous.file:  # 기존 자동저장 파일이 있는 경우에만 진행.
                previous_file_path = previous.file.path
                new_file_path = self.file.path
                previous_file_time = os.path.getmtime(previous_file_path)
                new_file_time = os.path.getmtime(new_file_path)
                if previous_file_time == new_file_time:  # 임시저장에서 정리가 1차례 되었으니, file값만 보면 됨.
                    pass
                else:
                    # 다르다면 기존 임시저장 파일 지우고 진행.
                    previous.file.delete(save=False)

        super(HomeworkAnswer, self).save(*args, **kwargs)
@receiver(pre_delete, sender=HomeworkAnswer)
def delete_homework_answer_file(sender, instance, **kwargs):
    # 모델 인스턴스(답변)가 삭제되기 전에 파일을 삭제합니다. 각 칼럼별로 모두.
    if instance.file:
        instance.file.delete(save=False)
    if instance.auto_file:
        instance.auto_file.delete(save=False)

class AnnounceBox(BaseBox):
    pass
class Announcement(UnderBox):
    announce_box = models.ForeignKey('AnnounceBox', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="Announce_author")
    author_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    # 버려질 속성들.
    homeroom = models.ForeignKey('Homeroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 학급.
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, null=True, blank=True)  # 공지할 교실.
    def __str__(self):
        return self.subject
class AnnoIndividual(models.Model):
    '''개별적으로 전달되는 공지. 과제랑 하나의 모델로 엮어도 크게 문제는 없지 않나? 과제에 announcement를 다는 방식으로.'''
    base_announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE)
    to_student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)  # 각 개별 학생에게 전달되게끔.  # 프로필 완성되면 지우자.
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True,
                                   default=None  # 이건 모델 정리되면 지워도 될듯.
                                   )  # 학교 프로필에 전달하게끔.
    content = models.TextField(default=None, null=True, blank=True)  # 공지 내용.
    read = models.BooleanField(default=False)  # 열람했는지 여부.
    check = models.BooleanField(default=False)  # 확인 했는지 여부.
    check_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.to_profile.name