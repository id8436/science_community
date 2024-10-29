from django.contrib import admin
from .models import *


admin.site.register(School) #모델을 등록한다.
admin.site.register(Homeroom)
admin.site.register(Subject)
admin.site.register(Classroom)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Announcement)
admin.site.register(AnnounceBox)
admin.site.register(AnnoIndividual)
admin.site.register(Homework)
admin.site.register(HomeworkQuestion)
#admin.site.register(HomeworkSubmit)
class HomeworkSubmitAdmin(admin.ModelAdmin):
    search_fields = ['target_profile__name']  # 제목과 저자 이름으로 검색 가능
admin.site.register(HomeworkSubmit, HomeworkSubmitAdmin)
#admin.site.register(HomeworkAnswer)
class HomeworkAnswerAdmin(admin.ModelAdmin):
    search_fields = ['target_profile__name']  # 제목과 저자 이름으로 검색 가능
admin.site.register(HomeworkAnswer, HomeworkAnswerAdmin)
admin.site.register(HomeworkBox)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin')
admin.site.register(Profile, ProfileAdmin)



