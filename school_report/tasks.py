from celery import shared_task
from . import models
from .view.special import ai_completion
@shared_task
def api_answer(df, homework, school, ai_models):
    import json
    import pandas as pd
    homework.is_end = True  # pending
    homework.save()

    # 질문 목록 획득.
    question_list = []
    for question in df.columns[2:]:
        question = models.HomeworkQuestion.objects.get(homework=homework, question_title=question)
        question_list.append(question)
    # 열 순회.
    for index in df.index:
        row = df.loc[index]
        try:  # 제대로 된 데이터인지.
            student = models.Student.objects.get(school=school, student_code=int(row['학번']))
            submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_user=student.admin)
        except:
            # messages.error(request, '적절하지 않은 학번의 경우 건너뜁니다. ' + str(row[0]))
            continue
        # ai에 넣을 텍스트 제작.
        input_text = ''
        for question in question_list:
            input_text += question.question_title + ':' + str(row[question.question_title]) + '\n'
        # 학생의 과제 제출 객체 획득.

        try:
            work_df = pd.read_json(submit.content)  # 기존 과제 추출.
        except:
            work_df = pd.DataFrame({'계정': [student.admin], '제출자': [student.name], '학번': [student.student_code]})
            work_df = work_df.set_index('계정')  # 인덱스로 만든다.
        for ai_model in ai_models:
            match ai_model:
                case 'gpt-3.5-turbo' | 'gpt-4':
                    response = ai_completion.gpt_chat_response(ai_model, input_text)
                case 'text-davinci-003' | 'text-curie-003':
                    response = ai_completion.gpt_response(ai_model, input_text)
            work_df[ai_model] = response
            submit.content = work_df.to_json(orient='records')
            submit.save()
    homework.is_end = False
    homework.save()