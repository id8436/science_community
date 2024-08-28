from django import template
register = template.Library()
@register.inclusion_tag('school_report/main_object_list.html', takes_context=True)
def objects_order_by_profile_activated(context):
    return_dict = {}
    request = context['request']
    return_dict['profiles'] = request.user.school_profile.all().order_by('-activated')
    return return_dict