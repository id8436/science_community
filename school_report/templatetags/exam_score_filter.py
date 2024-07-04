from boards.models import Exam_profile
from django import template
from school_report.view import check
from boards.models import Subject
register = template.Library()
@register.inclusion_tag('boards/score/exam_teacher_manu_filter.html', takes_context=True)
def teacher_manu(context):
    return_dict = {}
    request = context['request']
    board = context['board']
    return_dict['board'] = board
    school = board.school
    teacher = check.Teacher(user=request.user, school=school).in_school_and_none()
    return_dict['teacher'] = teacher
    subjects = Subject.objects.filter(base_exam=board)
    return_dict['subjects'] = subjects
    return return_dict