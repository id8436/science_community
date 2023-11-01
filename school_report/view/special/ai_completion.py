from custom_account.decorator import custom_login_required as login_required
from django.shortcuts import render, get_object_or_404, redirect
from school_report.view.classroom import make_spreadsheet_df
from django.contrib import messages
from school_report import models  # 모델 호출.
from school_report import tasks
import pandas as pd
@login_required()
def spreadsheet_to_ai(request, posting_id):
    '''세특 작성을 위한... ai의 연산 시작'''
    # ai가 작동중일 땐
    df = make_spreadsheet_df(request, posting_id)
    # 답변은 submit의 content에 json으로 저장해도 괜찮을듯? 아니, 그럼 모델을 추가해서 살펴볼 때 지워지지 않나? 아니면... df로 복원한 다음 다루는 것도 괜찮을듯.
    homework = get_object_or_404(models.Homework, id=posting_id)
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    if homework.subject_object:
        school = homework.subject_object.school

    ai_models = request.POST.getlist('ai_model')  # 사용자가 선택한 모델들.
    print('delay로 들어갑니다.')
    #나중에 아래 함수의 delay 속성으로 진행하자.
    if homework.is_end == True:
        messages.error(request, '기존에 요청한 작업을 진행중입니다.')
        return redirect(request.META.get('HTTP_REFERER', None))
    else:
        tasks.api_answer(df, homework, school, ai_models)  # 정보를 주고 task에서 수행.

    return redirect(request.META.get('HTTP_REFERER', None))
@login_required()
def read_response(request, posting_id):
    '''ai가 써준 세특 초안을 보여주는 기능.'''
    homework = get_object_or_404(models.Homework, id=posting_id)
    if request.user == homework.author:
        pass
    else:
        messages.error(request, '작성자만 열람할 수 있습니다.')
        return redirect(request.META.get('HTTP_REFERER', None))
    submits = models.HomeworkSubmit.objects.filter(base_homework=homework)
    context = {}
    merged_df = pd.DataFrame()
    for submit in submits:
        try:
            work_df = pd.read_json(submit.content)  # 기존 과제 추출.
        except:
            continue  # 기록된 게 없으면 건너뛰자.
            # work_df = work_df.set_index('계정')  # 인덱스로 만든다.
        merged_df = pd.concat([merged_df, work_df], axis=0, ignore_index=True)
    context['data_list'] = merged_df.to_dict(orient='records')
    if homework.is_end == True:
        messages.error(request, '아직 ai의 작업이 진행중입니다.')
    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', context)

role = '''
너는 대한민국의 교사야. 학생들을 평가해서 과목별 세부능력 특기사항을 기록할거야.
기초 데이터는 '활동명:활동내용' 형식으로 모았어.
아래의 조건에 따라 글을 정리해줘.
조건
- 객관적인 사실을 기입했다는 느낌으로.
- 주어는 빼고.
- 모든 어미는 음슴체로 끝낼 것.(~함, ~임, ~음)

아래 예시와 비슷한 느낌으로 정리해줘.
"교과서의 연습 문제를 풀며 다양한 방식의 풀이를 탐구하게 되고 탐구 중에 뉴턴역학 외에 라그랑주 역학, 헤밀턴 역학이 있다는 사실을 알게 되어 이에 대해 탐구하여 발표함. 역학에서의 작용이 항상 최소가 된다는 것에 의문을 느끼고 컴퓨터가 효율을 높이게끔 발달하듯 자연이 최적의 효율로 움직이려 한다는 해석을 제시함. 뉴턴역학과 다른 철학, 과정을 거친 풀이가 같은 결과를 낸다는 것에 흥미를 느끼고 과거 학자들의 창의성에 감탄했다는 소감을 남김. 이러한 역학 체계가 분자의 운동과 반응 예측, 신약개발에서 약 분자와 표적 단백질이 어떻게 반응하고 결합하는지에 대해서도 쓰인다는 것을 알고 추후 더 깊이 공부해보고 싶다는 소감을 남김."
'''
def gpt_response(ai_model, input_text):
    import openai
    openai.api_key = "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"
    # 조건
    model = ai_model  # 선택할 수 있게! ex) gpt-3.5-turbo
    import tiktoken
    tokenizer = tiktoken.Tokenizer()
    tokens = tokenizer.tokenize(input_text)
    max_tokens = len(tokens) + 700  # 출력은 700 이하가 되게끔.

    match ai_model:
        case 'gpt-3.5-turbo' | 'gpt-4':
            response = openai.Completion.create(engine=model,
                prompt=role, max_tokens=max_tokens)
            response = response['choices'][0]['text']
        case 'text-davinci-003' | 'gpt-3.5-turbo-instruct':
            messages = [{'role': 'system',
                         'content': role},
                        {'role': 'user',
                         'content': input_text}, ]
            response = openai.ChatCompletion.create(model=model,
                messages=messages, max_tokens=max_tokens)
            response = response['choices'][0]['message']['content']
    # 반
    print(max_tokens)
    print(response)
    print('답변')
    response = response.replace('\n', '<br>')  # 탬플릿에서 줄바꿈이 인식되게끔.
    print(response)
    return response