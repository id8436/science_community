from django import template
from custom_account.models import Notification

register = template.Library()

@register.inclusion_tag('custom_account/notification.html', takes_context=True)
def show_notifications(context):
    to_user = context['request'].user
    notifications = Notification.objects.filter(to_user=to_user)
    notifications = notifications.order_by('-created_date')
    return {'notifications':notifications}