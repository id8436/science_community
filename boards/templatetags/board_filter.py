from boards.models import Exam_profile
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
    try:
        exam_profile = Exam_profile.objects.get(master=user, base_exam=base_exam)
        return_dict['exam_profile'] = exam_profile
    except:
        pass
    return return_dict