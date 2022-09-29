from boards.models import Exam_profile
from django import template

register = template.Library()
@register.inclusion_tag('boards/score/exam_profile_filter.html', takes_context=True)
def show_exam_profile(context):
    user = context['request'].user
    base_exam = context['board']
    exam_profile = Exam_profile.objects.filter(master=user, base_exam=base_exam)[0]
    return {'exam_profile':exam_profile, 'board':base_exam}