from .. import models
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

class Check_teacher:
    def __init__(self, request, var):
        self.model = models.Teacher
        self.messase_school = "이 학교에 소속된 교사가 아닙니다."
        self.messase_homeroom = "이 학급의 마스터가 아닙니다."
        self.request = request
        self.var = var  # 학교가 들어올지, 학급이 들어올지 모르지.
    def check_in_school(self):
        try:
            obj = self.model.objects.filter(school=self.var, admin=self.request.user).last()  # 여러개가 있을 경우 가장 나중.
            return obj
        except:
            return False
    def check_in_homeroom(self):
        pass  # 필요할 때 구현해보자.

    def in_school_and_none(self):
        if self.check_in_school():
            return self.check_in_school()
        else:
            return None
    def in_school_and_redirect_to_school(self):
        if self.check_in_school():
            return self.check_in_school()
        else:
            messages.error(self.request, self.messase_school)
            return redirect('school_report:school_main', school_id=self.var.id)  # 필요에 따라 렌더링.

class Check_student(Check_teacher):
    '''클래스를 상속하는 방식이라면 간편하다.'''
    def __init__(self, request, var):
        super().__init__(request, var)
        self.model = models.Student
        self.messase_school = "이 학교에 소속된 학생이 아닙니다."
        self.messase_homeroom = "이 학급의 학생이 아닙니다."