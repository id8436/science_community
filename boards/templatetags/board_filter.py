from boards.models import Exam_profile
from django import template

register = template.Library()
@register.inclusion_tag('boards/score/exam_profile_filter.html', takes_context=True)
def show_exam_profile(context):
    return_dict = {}
    user = context['request'].user
    base_exam = context['board']
    return_dict['board'] = base_exam
    exam_profile, created = Exam_profile.objects.get_or_create(master=user, base_exam=base_exam)
    return_dict['exam_profile'] = exam_profile
    if base_exam.subject_set.exists():
        return_dict['registered'] = True
    return return_dict