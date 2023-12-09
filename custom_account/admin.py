from django.contrib import admin
from .models import User, Notification, Debt  # 직접 등록한 모델

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'email')
    exclude = ('password',)  # 사용자 상세 정보에서 비밀번호 필드를 노출하지 않음
admin.site.register(Notification)
admin.site.register(Debt)