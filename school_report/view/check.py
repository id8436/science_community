from .. import models
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

class Teacher:
    '''가변인자로 구성하여 활용이 쉽게 해보자.'''
    def __init__(self, **kwargs):
        '''다음과 같은 변수들을 받았을 때 적절히 작동하도록 해보자. 필요변수들은 생성 시에 받도록. user, request,
        school, homeroom, classroom
        '''
        self.args = kwargs
        # self.model = models.Teacher  # 없애갈 것.
        self.message_school = "이 기관에 소속된 교사가 아닙니다."
        self.message_homeroom = "이 학급의 마스터가 아닙니다."
        self.message_classroom = "이 교과의 관리자가 아닙니다."
        self.position = 'teacher'  # 학생 모델은 이걸 상속해서 보여주니까. 포지션만 다르게 지정.
    def in_school(self):
        '''검사 후 메시지도.'''
        # 필요 변수 설정.
        user = self.args.get('user')
        school = self.args.get('school')
        # 판단.
        check = True
        try:  # 프로필이 없거나.
            profile = models.Profile.objects.filter(admin=user, school=school).last()  # 나중에 정리 되면 get으로 바꾸자. # 여러개가 있을 경우 가장 나중.
            profile.position  # None이면 에러가 뜸.
        except:
            request = self.args.get('request')
            if request:
                messages.error(request, self.message_school)
            return None
        if profile.position != self.position:  # 학생프로필로 들어온 경우도 처리.
            check = None
        # 판단 후처리.
        if check == None:
            print(profile)
            request = self.args.get('request')
            if request:
                messages.error(request, self.message_school)
            return None
        return profile
    def in_homeroom(self):
        # 필요 변수 설정.
        user = self.args.get('user')
        homeroom = self.args.get('homeroom')
        #school = homeroom.school
        # 판단.
        check = True
        try:  # 프로필이 없거나.
            profile = models.Profile.objects.filter(admin=user, homeroom=homeroom).last()  # 나중에 정리 되면 get으로 바꾸자. # 여러개가 있을 경우 가장 나중.
            profile.position  # None이면 에러가 뜸.
        except:
            request = self.args.get('request')
            if request:
                messages.error(request, self.message_homeroom)
            return None
        if profile.position != self.position:  # 학생프로필로 들어온 경우도 처리.
            check = None
        # 판단 후처리.
        if check == None:
            request = self.args.get('request')
            if request:
                messages.error(request, self.message_homeroom)
            return None
        return profile
    def check_in_classroom(self):
        try:
            obj = self.model.objects.filter(homeroom=self.organization, admin=self.request.user).last()  # 여러개가 있을 경우 가장 나중.
            return obj
        except:
            return False
    #### 단순히 검사만 하고 아무것도 안하고 싶을 때.
    def in_school_and_none(self):
        '''단순히 검사만 하고 아무것도 안하고 싶을 때.'''
        # 필요 변수 설정.
        user = self.args.get('user')
        school = self.args.get('school')
        # 판단.
        try:  # 프로필이 없거나.
            profile = models.Profile.objects.filter(admin=user, school=school).last()  # 나중에 정리 되면 get으로 바꾸자. # 여러개가 있을 경우 가장 나중.
            profile.position  # None이면 에러가 뜸.
        except:
            return None
        if profile.position != self.position:  # 학생프로필로 들어온 경우도 처리.
            return None
        return profile
    def in_homeroom_and_none(self):
        '''단순히 검사만 하고 아무것도 안하고 싶을 때.'''
        # 필요 변수 설정.
        user = self.args.get('user')
        homeroom = self.args.get('homeroom')
        # 판단.
        try:  # 프로필이 없거나.
            profile = models.Profile.objects.filter(admin=user, homeroom=homeroom).last()  # 나중에 정리 되면 get으로 바꾸자. # 여러개가 있을 경우 가장 나중.
            profile.position  # None이면 에러가 뜸.
        except:
            return None
        if profile.position != self.position:  # 다른 프로필로 들어온 경우도 처리.
            return None
        return profile

    #### redirect류를 쓰려면 request를 넣어주어야 한다.
    def redirect_to_school(self):
        # 필요 변수 설정.
        school = self.args.get('school')
        return redirect('school_report:school_main', school_id=school.id)  # 필요에 따라 렌더링.
    def redirect_to_homeroom(self):
        messages.error(self.request, self.message_homeroom)
        return redirect('school_report:homeroom_main', homeroom_id=self.organization.id)  # 필요에 따라 렌더링.
    def redirect_to_classroom(self):
        messages.error(self.request, self.message_classroom)
        return redirect('school_report:classroom_main', classroom_id=self.organization.id)  # 필요에 따라 렌더링.


class Student(Teacher):
    '''클래스를 상속하는 방식이라면 간편하다.'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = models.Student  # 요것도 변경..!
        self.message_school = "이 기관에 소속된 학생이 아닙니다."
        self.message_homeroom = "이 학급의 학생이 아닙니다."
        self.message_classroom = "이 교과의 학생이 아닙니다."
        self.position = 'student'
    # 교사 클래스를 상속하여 그대로 구현했으니, 이게 완성버전.
