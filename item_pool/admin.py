from django.contrib import admin
from .models import Question,Answer, School, Grade, ImageInQuestion #모델을 불러오고

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']
admin.site.register(Question,QuestionAdmin) #모델을 등록한다.

admin.site.register(Answer) #모델을 등록한다.
admin.site.register(School)  # 학교모델
admin.site.register(Grade)  # 학년모델
admin.site.register(ImageInQuestion)

