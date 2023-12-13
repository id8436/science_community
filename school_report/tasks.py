from celery import shared_task
from . import models
from .view.special import ai_completion
from custom_account.view import payment
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

@shared_task
def api_answer(request_user_id, posting_id, ai_models, contents_list, submit_id_list, total_charge):
    '''테스크 처리.'''
    #  시작하기 전에 점검부터

    # 들어오기 직전 밖에서도 이 작업을 거치긴 하는데...
    #contents_list, submit_list = make_ai_input_data(posting_id, pk_list)

    # submit에 내용 저장할 때 정보를 담기 위해 school이 필요해서.
    homework = models.Homework.objects.get(id=posting_id)
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    if homework.subject_object:
        school = homework.subject_object.school
    homework.is_end = False  # False = pending
    homework.save()

    # 학생의 과제 제출 객체 획득, 변경.
    import pandas as pd
    for input_text, submit_id in zip(contents_list, submit_id_list):
        submit = models.HomeworkSubmit.objects.get(id=submit_id)
        try:
            work_df = pd.read_json(submit.content)  # 기존 과제 추출.
        except:
            student = models.Student.objects.get(school=school, admin=submit.to_user)
            work_df = pd.DataFrame({'계정': [student.admin], '제출자': [student.name], '학번': [student.student_code]})
            work_df = work_df.set_index('계정')  # 인덱스로 만든다.
        for ai_model in ai_models:
            match ai_model:
                case 'gpt-3.5-turbo' | 'gpt-4'|'text-davinci-003' | 'text-curie-003' | 'gpt-3.5-turbo-instruct'|'gpt-4-1106-preview':
                    response = ai_completion.gpt_response(ai_model, input_text)
            work_df[ai_model] = response
            submit.content = work_df.to_json(orient='records')
            submit.save()


    # 나중에 여기에 빛, 혹은 point 넣자.
    homework.is_end = True
    homework.save()
    # 나중에 작업 끝날 때 정산.
    cause_text = str(len(contents_list)) + "건에 대한 AI 연산."
    user = get_object_or_404(get_user_model(), id=request_user_id)
    payment.payment(user=user, amount=total_charge, cause=cause_text)