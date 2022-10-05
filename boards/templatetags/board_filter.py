from boards.models import Exam_profile
from django import template

register = template.Library()
@register.inclusion_tag('boards/score/exam_profile_filter.html', takes_context=True)
def show_exam_profile(context):
    user = context['request'].user
    base_exam = context['board']
    exam_profile, created = Exam_profile.objects.get_or_create(master=user, base_exam=base_exam)
    return {'exam_profile':exam_profile, 'board':base_exam}