from django.contrib import admin
from .models import *


admin.site.register(School) #모델을 등록한다.
admin.site.register(Homeroom)
admin.site.register(Classroom)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Announcement)
admin.site.register(AnnoIndividual)

