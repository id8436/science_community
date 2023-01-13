from celery import shared_task

# 교정을 위한 모듈 임포트.
from utility.models import Spell, SpellObject

@shared_task
def correct_text(user_id, inner_data):
    from django.contrib.auth import get_user_model
    from utility.language.korean_spell.korean_spell import han_spell
    import json
    user = get_user_model().objects.get(pk=user_id)
    try:  # 객체가 없다면 에러를 반환하니까.
        origin_user = Spell.objects.get(user=user)  # 기존에 있었던 모델을 가져온다.
        origin_user.delete()  # 기존 모델 지우기.
    except:
        pass
    # 이 함수로 들어오기 전에 위에서 처리함.
    # try:  # 객체가 없다면 에러를 반환하니까.
    #     origin_user = Spell.objects.get(user=user)  # 기존에 있었던 모델을 가져온다.
    #     origin_user.delete()  # 기존 모델 지우기.
    # except:
    #     pass

    try:
        json_data = json.loads(inner_data)
        spell_user = Spell.objects.create(user=user, status='진행중', how_many=len(json_data))
        for text in json_data:
            cor_num, corrected_text = han_spell(text)  # 셀의 데이터를 교정처리한다.
            if cor_num > 0:  # 수정이 있었다면 내용을 담는다.
                SpellObject.objects.create(spell=spell_user, origin_text=text, corrected_text=corrected_text)

            spell_user.now_going_on += 1  # 한 줄 진행에 하나씩 더하기.
            spell_user.save()  # 진행상황 저장.

        spell_user.status = '처리 완료'
        spell_user.save()  # 진행상황 저장.
    except Exception as e:
        spell_user.status = '에러 발생'
        spell_user.message = str(e)  # 에러메시지를 담는다.
        spell_user.save()
    # 잘못된 내용이 있다면 해당 정보를 담아서 반환. DB에 저장하므로 따로 반환할 필요는 없음.