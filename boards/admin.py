from django.contrib import admin
from .models import Posting, Tag, Board, Board_name, Board_category, Exam_profile, Score

class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'board_name',)
admin.site.register(Board, BoardAdmin)

admin.site.register(Board_name)

class Board_categoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
admin.site.register(Board_category, Board_categoryAdmin)

admin.site.register(Posting)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Tag, TagAdmin)

admin.site.register(Exam_profile)
admin.site.register(Score)
# Register your models here.
