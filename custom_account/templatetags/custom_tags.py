from django import template
from custom_account.models import Notification
from django.shortcuts import redirect
register = template.Library()

@register.inclusion_tag('custom_account/notification.html', takes_context=True)
def show_notifications(context):
    to_user = context['request'].user
    base_notifications = Notification.objects.filter(to_user=to_user)
    notifications = base_notifications.filter(official=False).order_by('-created_date')[:7]
    official_notifications = base_notifications.filter(official=True).order_by('-created_date')[:7]
    return {'notifications':notifications, 'official_notifications':official_notifications}

@register.inclusion_tag('custom_account/warning_social_account.html', takes_context=True)
def check_social(context):  # 접속한 사람이 소셜계정을 연동하지 않고 다른 링크로 부정접근할 경우.
    user = context['request'].user
    dict = {}
    try:
        if user.is_social:
            dict['social_account'] = True
            dict['range'] = range(100)
    except:
        pass
    return dict

@register.filter
def split(value, delimiter=" "):
    return value.split(delimiter)