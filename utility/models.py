from django.db import models
from django.conf import settings

class Spell(models.Model):
    '''맞춤법 검사기 실행 관련 모델'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spell_user')
    status = models.CharField(max_length=10)
    how_many = models.IntegerField()  # 총 몇개의 텍스트를 살필 것인가.
    now_going_on = models.IntegerField(default=0)  # 현재 진행된 텍스트 갯수.
    message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)  # 실행시간.

class SpellObject(models.Model):
    '''맞춤법 검사 대상. spell 아래에 귀속되는 형태로.'''
    spell = models.ForeignKey('Spell', on_delete=models.CASCADE)  # 기준으로 삼을 모델.
    origin_text = models.TextField(blank=True)
    corrected_text = models.TextField(blank=True)

class DataObject(models.Model):
    '''데이터검사의 기초'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_user')
    info = models.TextField(null=True)  # 분명 만들 때 기입되는 내용인데;; 종종 정보가 없는 경우가;;;
    contents = models.TextField()
    created = models.DateTimeField(auto_now_add=True)  # 실행시간.
    # 각종 통계 결과치.
    correlation = models.TextField(null=True, blank=True)