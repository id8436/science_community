from boards.models import Exam_profile
from school_report.models import Profile
from school_report.view import check
from django import template

def create_random_name(length):
    import string
    import random
    length = length  # 10자리
    string_pool = string.ascii_letters + string.digits # 대소문자
    result = ""  # 결과 값
    for i in range(length):
        result += random.choice(string_pool)  # 랜덤한 문자열 하나 선택
    return result

register = template.Library()
@register.inclusion_tag('boards/score/exam_profile_filter.html', takes_context=True)
def show_exam_profile(context):
    return_dict = {}
    user = context['request'].user
    base_exam = context['board']
    return_dict['board'] = base_exam
    # 프로필 지정.
    exam_profile = Exam_profile.objects.filter(master=user, base_exam=base_exam).last()
    if exam_profile:
        return_dict['exam_profile'] = exam_profile
        if exam_profile.official:
            pass
        else:
            student = check.Student(user=user, school=base_exam.school).in_school_and_none()
            if student:  # 기존 프로파일이 있다면 연결.
                new_pro, created = Exam_profile.objects.get_or_create(test_code=student.code, base_exam=base_exam)
                new_pro.master = student.admin  # 관리자 덮어써주고~
                new_pro.student = student
                new_pro.name = student.name
                new_pro.official = True
                new_pro.save()
    else:  # 프로필이 없을 때.  # 위와 동일.
        student = check.Student(user=user, school=base_exam.school).in_school_and_none()
        if student:
            new_pro, created = Exam_profile.objects.get_or_create(test_code=student.code, base_exam=base_exam)
            new_pro.master = student.admin  # 관리자 덮어써주고~
            new_pro.student = student
            new_pro.name = student.name
            new_pro.official = True
            new_pro.save()
    return return_dict