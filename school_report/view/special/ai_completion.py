from custom_account.decorator import custom_login_required as login_required
from django.shortcuts import render, get_object_or_404, redirect
from school_report.view.classroom import make_spreadsheet_df
from django.contrib import messages
from school_report import models  # 모델 호출.
from school_report import tasks
import pandas as pd
import math
from django.contrib.auth import get_user_model
from custom_account.models import Debt
import openai

@login_required()
def spreadsheet_to_ai(request, posting_id):
    '''세특 작성을 위한... ai의 연산 시작'''
    # ai가 작동중일 땐
    df = make_spreadsheet_df(request, posting_id)  # 스프레드시트의 df
    # 답변은 submit의 content에 json으로 저장해도 괜찮을듯? 아니, 그럼 모델을 추가해서 살펴볼 때 지워지지 않나? 아니면... df로 복원한 다음 다루는 것도 괜찮을듯.
    homework = get_object_or_404(models.Homework, id=posting_id)
    # 아래는 pk와 id를 직접 넣으면서 필요없어진 부분.
    # if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
    #     school = homework.classroom.school
    # if homework.subject_object:
    #     school = homework.subject_object.school

    # 가격 계산 앞부분과 동일.
    pk_list = request.POST.getlist("pk_checks")
    token_num = int(request.POST.get('token_num'))
    # classroom.py의 스프레드시트 df 만들기와 유사하게.
    contents_list, submit_id_list = make_ai_input_data(posting_id, pk_list)
    ai_models = request.POST.getlist('ai_model')  # 사용자가 선택한 모델들.

    total_charge = count_ai_use_point(request, contents_list, ai_models, token_num)
    #나중에 아래 함수의 delay 속성으로 진행하자.
    if type(total_charge) == type(redirect(request.META.get('HTTP_REFERER', None))):
        return redirect(request.META.get('HTTP_REFERER', None))
    if homework.is_end == False:
        messages.error(request, '기존에 요청한 작업을 진행중입니다.')
        return redirect(request.META.get('HTTP_REFERER', None))
    else:
        tasks.api_answer.delay(request.user.id, posting_id, ai_models, contents_list, submit_id_list, total_charge, token_num)  # 정보를 주고 task에서 수행.
        #tasks.api_answer(request.user.id, posting_id, ai_models, contents_list, submit_id_list, total_charge, token_num)  # 정보를 주고 task에서 수행.
    messages.info(request, '작업을 수행합니다. 데이터에 따라 수행 시간이 달라집니다.')
    messages.info(request, '예상 소요 포인트: '+str(total_charge))
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
    if homework.is_end == False:  # 작업진행여부 불리언.
        messages.error(request, '아직 ai의 작업이 진행중입니다.')
    debts = Debt.objects.filter(user=request.user, is_paid=False)
    if debts:
        total_debt = 0  # 빚 알려주기용.
        for debt in debts:
            total_debt += debt.amount
        messages.error(request, "당신은 빚쟁이에요~!  "+str(total_debt)+"포인트")
    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', context)
@login_required()
def info_how_much_point_taken(request, posting_id):
    '''포인트가 얼마나 들지 계산하고 반환.'''
    pk_list = request.POST.getlist("pk_checks")
    token_num = int(request.POST.get('token_num'))
    # classroom.py의 스프레드시트 df 만들기와 유사하게.

    contents_list, submit_id_list = make_ai_input_data(posting_id, pk_list)
    ai_models = request.POST.getlist('ai_model')  # 사용자가 선택한 모델들.

    total_charge = count_ai_use_point(request, contents_list, ai_models, token_num)  # 정보를 주고 task에서 수행.

    messages.info(request, '예상 포인트: '+str(total_charge))
    return redirect(request.META.get('HTTP_REFERER', None))
def make_ai_input_data(posting_id, pk_list):
    homework = get_object_or_404(models.Homework, id=posting_id)
    # 바로 pk로 가져오면서 필요없어진 부분.
    # if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
    #     school = homework.classroom.school
    # if homework.subject_object:
    #     school = homework.subject_object.school
    # 아예 df로 pk와 콘텐츠 데이터 담아 보내기.(ai 처리엔 submit 리스트를 직접 보내는 것도 좋지 않을까??)
    question_list = homework.homeworkquestion_set.order_by('ordering')
    contents_list = []  # 질문과 답변을 모은 개인 전체 텍스트를 담을 리스트.
    submit_list = []  # 대상 학생의 submit리스트.
    submit_id_list = []  # task에 올릴 때 json화 해야 하는데, 모델을 보낼 수 없어..ㅜ
    for pk in pk_list:
        if pk == None:
            continue  # 유저모델에 대한 정보 없으면 다음으로 넘기게끔.
        response_user = get_object_or_404(get_user_model(), id=pk)
        submit = models.HomeworkSubmit.objects.get(to_user=response_user, base_homework=homework)
        submit_list.append(submit)
        submit_id_list.append(submit.id)
        content = ''  # 텍스트를 담을...
        for question in question_list:
            try:
                answer = models.HomeworkAnswer.objects.get(question=question,
                                                           respondent=response_user)  # 해당 질문에 대한 답변들 모음.
                content += question.question_title + ":"
                content += answer.contents + "\n"  # 답변 담고 내리기.
            except:
                pass
        contents_list.append(content)
    return contents_list, submit_id_list
def count_ai_use_point(request, contents_list, ai_models, token_num):
    '''모델을 사용함에 있어 포인트가 얼마나 들지 파악.(결제할 때에도 이용.)'''
    from school_report.view.special.ai_model_info_list import price_list, max_tocken_list
    total_charge = 0  # 여기에 총 금액을 담아 반환한다.

    # 아래 다 문제 없으면 지우자.
    # 온전한 텍스트를 df에 합쳐 넣어서 없어도 되는 부분. 질문 목록 획득.
    # question_list = []
    # for question in df.columns[1:]:
    #     question_list.append(question)
    # 마찬가지로 온전한 텍스를 만들어서 오기 때문에 필요 없음. 열 순회.
    # for index in df.index:
    #     row = df.loc[index]
    #     # ai에 넣을 텍스트 제작.
    #     input_text = ''
    #     for question in question_list:
    #         input_text += question + ':' + str(row[question]) + '\n'
    #     text_list.append(input_text)  # 최종 text_list에 합치기.

    for ai_model in ai_models:
        # GPT의 경우 모델별로 인코딩 방법이 조금씩 다름.
        import tiktoken
        try:
            encoding = tiktoken.encoding_for_model(ai_model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        # for index in df.index:
        #     row = df.loc[index]
        for text in contents_list:
            num_tokens = len(encoding.encode(text + role))  # 프롬프트 입력값까지 고려해야 해.
            print('토큰갯수')
            print(num_tokens + token_num)
            if (num_tokens + token_num) >= max_tocken_list[ai_model]:  # 글자수 제한 반려.
                messages.error(request, '선택하신 '+ai_model +'은 입력 및 출력 데이터의 합이 '+str(max_tocken_list[ai_model])+'을 넘을 수 없습니다.')
                return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
            tokens_for_count = (num_tokens + token_num) / 1000  # 복사용 토큰. 1천개당 계산을 위해 정리.  # 반환토큰까지 고려.
            tokens_for_count = math.ceil(tokens_for_count)  # 올림 처리. 1000개 당 가격을 매기기 위해.
            price_per_1000 = price_list[ai_model]  # 1000토큰 당 가격 가져오기.
            total_charge += (tokens_for_count) * price_per_1000
    return total_charge


import google.generativeai as genai
from config.secret import Google_AI_KEY

role = '''너는 대한민국의 교사로, 학생들의 활동을 평가하고 세부능력, 특기사항을 기록할 것임. 활동 데이터는 '활동명:활동내용'의 형식으로 제공됨. 다음의 까다로운 요구사항에 따라 글을 작성해야 함:
- 객관적인 사실만 기입.
- 주어를 빼고 작성.
- 모든 문장은 음슴체로 끝나야 함 (~함, ~임, ~음).
- 중복되는 내용은 제외.
- 한 문단으로 작성.

다음은 활동 데이터 예시임:
"교과서의 연습 문제를 풀면서 다양한 방식의 풀이를 탐구하며 뉴턴역학 외에 라그랑주 역학, 헤밀턴 역학이 있다는 사실을 알게 됨. 역학에서의 작용이 항상 최소가 된다는 것에 의문을 느끼고, 컴퓨터가 효율을 높이게끔 발달하듯 자연이 최적의 효율로 움직이려 한다는 해석을 제시함. 뉴턴역학과 다른 철학, 과정을 거친 풀이가 같은 결과를 낸다는 것에 흥미를 느꼈다는 소감을 남김."
위 조건을 토대로 적절한 세부능력 및 특기사항을 기록해보아라. 다음은 작성 기초 데이터들이다.'''
max_tokens = 700
def gpt_response(ai_model, input_text, token_num):
    '''ai에 던지고 응답을 받는 본 기능.'''
    from config.secret import GPT_KEY  # API 키는 비밀로 보관.
    openai.api_key = GPT_KEY

    from school_report.view.special.ai_model_info_list import mechanism_list
    # GPT 모델에만 해당하는 채팅, 완성 구분.
    match mechanism_list[ai_model]:
        case 'Completion':
            response = openai.Completion.create(engine=ai_model,
                prompt=role+input_text, max_tokens=token_num)
            response = response['choices'][0]['text']
        case 'ChatCompletion':
            messages = [{'role': 'system',
                         'content': role},
                        {'role': 'user',
                         'content': input_text}, ]
            response = openai.ChatCompletion.create(model=ai_model,
                messages=messages, max_tokens=token_num)
            response = response['choices'][0]['message']['content']
    if ai_model == 'gemini-pro':  # 사실, 구글이지만... 큰 문제는 없으니..
        genai.configure(api_key=Google_AI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(role+input_text)
        response = response.text
    # 반
    response = response.replace('\n', '<br>')  # 탬플릿에서 줄바꿈이 인식되게끔.
    return response