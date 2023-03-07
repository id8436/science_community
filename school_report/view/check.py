from .. import models
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

class Check_teacher:
    def __init__(self, request, var):
        self.model = models.Teacher
        self.messase_school = "이 학교에 소속된 교사가 아닙니다."
        self.messase_homeroom = "이 학급의 마스터가 아닙니다."
        self.messase_classroom = "이 교과의 관리자가 아닙니다."
        self.request = request
        self.var = var  # 학교가 들어올지, 학급이 들어올지 모르지.
    def check_in_school(self):
        try:
            obj = self.model.objects.filter(school=self.var, admin=self.request.user).last()  # 여러개가 있을 경우 가장 나중.
            return obj
        except:
            return False
    def check_in_homeroom(self):
        try:
            obj = self.model.objects.filter(homeroom=self.var, admin=self.request.user).last()  # 여러개가 있을 경우 가장 나중.
            return obj
        except:
            return False
    def check_in_classroom(self):
        try:
            obj = self.model.objects.filter(homeroom=self.var, admin=self.request.user).last()  # 여러개가 있을 경우 가장 나중.
            return obj
        except:
            return False
    def in_school_and_none(self):
        if self.check_in_school():
            return self.check_in_school()
        else:
            return None

    def in_homeroom_and_none(self):
        if self.check_in_homeroom():
            return self.check_in_homeroom()
        else:
            return None
    def in_classroom_and_none(self):
        return self.in_homeroom_and_none()  # 교과는 학급에 종속되어 있으니까.
    def redirect_to_school(self):
        messages.error(self.request, self.messase_school)
        return redirect('school_report:school_main', school_id=self.var.id)  # 필요에 따라 렌더링.
    def redirect_to_homeroom(self):
        messages.error(self.request, self.messase_homeroom)
        return redirect('school_report:homeroom_main', homeroom_id=self.var.id)  # 필요에 따라 렌더링.
    def redirect_to_classroom(self):
        messages.error(self.request, self.messase_classroom)
        return redirect('school_report:classroom_main', classroom_id=self.var.id)  # 필요에 따라 렌더링.


class Check_student(Check_teacher):
    '''클래스를 상속하는 방식이라면 간편하다.'''
    def __init__(self, request, var):
        super().__init__(request, var)
        self.model = models.Student
        self.messase_school = "이 학교에 소속된 학생이 아닙니다."
        self.messase_homeroom = "이 학급의 학생이 아닙니다."
        self.messase_classroom = "이 교과의 학생이 아닙니다."
    # 교사 클래스를 상속하여 그대로 구현했으니, 이게 완성버전.
