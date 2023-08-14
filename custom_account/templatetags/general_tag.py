from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def store_current_url(context):
    request = context['request']
    if not request.user.is_authenticated:
        request.session['before_login'] = request.path
    return ''  # 탬플릿에 None이라고 떠서 문자열 반환이라도...