from django.shortcuts import render, get_object_or_404, redirect, resolve_url
import openpyxl
import requests
import json

def han_spell(text):
    # 0. 수정 데이터 담기.
    cor_num = 0  # 수정한 횟수.
    # 1. 텍스트 준비 & 개행문자 처리
    text = text.replace('\n', '\r\n')  # 개행문자를 검사기에 맞게 변경.
    # 2. 맞춤법 검사 요청 (requests)
    response = requests.post('http://164.125.7.61/speller/results', data={'text1': text})
    # 3. 응답에서 필요한 내용 추출 (html 파싱)
    data = response.text.split('data = [', 1)[-1].rsplit('];', 1)[0]  # 단순 데이터 찾기..
    try:
        # 4. 파이썬 딕셔너리 형식으로 변환
        data = json.loads(data)
    except:
        corrected_text = '없음.'
        return cor_num, corrected_text  # 에러가 생기면 바로 반환해버린다.(완벽하면 None이 반환됨.)
    # 5. 교정 내용 출력
    correction_datas = data['errInfo']
    corrected_text = text  # 흐흠, 어째서인지 이렇게 해도 복사가 된다. 편하네.
    pointer = 0  # 기본 개념과는 다르지만... 문자열을 삭제하고 나면 이동해야 할 포인터.
    # print(correction_datas)
    for correction_data in correction_datas:
        # 정보 받기.
        start = pointer + correction_data['start']  # 원문의 어디에서 시작하는지.
        end = pointer + correction_data['end']  # 원문의 어디에서 끝나는지.
        target = correction_data['orgStr']  # 문제가 있는 부분.
        help = correction_data['help']  # 무엇이 잘못된 것인지.
        changed = correction_data['candWord']  # 고쳐진 말.
        changed = '<span class="text-bg-danger opacity-75" title="{}">{}</span>'.format(help, changed)  # html처리.
        # 조작.
        # print(correction_data['orgStr'])
        corrected_text = corrected_text[:start] + changed + corrected_text[end:]  # 잘못된 용어 제거 + 교정어 삽입
        erased_len = len(changed) - len(target)
        pointer = pointer + erased_len  # 지워진 문자 만큼 포인터를 옮겨준다. 다음 문자열 제거를 위해서.
        # 문제정보 담기.
        cor_num += 1  # 수정횟수 증가.
    return cor_num, corrected_text

def main(request):
    context = {}

    return render(request, 'utility/korean_spell/main.html', context)



def upload_excel_form(request):
    if request.method == "POST":
        uploadedFile = request.FILES["uploadedFile"]  # post요청 안의 name속성으로 찾는다.
        wb = openpyxl.load_workbook(uploadedFile, data_only=True)  # 파일을 핸들러로 읽는다.
        sheetnames = wb.sheetnames
        work_sheet = wb[sheetnames[0]]  # 첫번째 워크시트를 사용한다.

        context = {}
        # 엑셀 데이터를 처리한다.
        wrong_text = {}
        for row in work_sheet.rows:  # 열을 순회한다.
            for cell in row:
                cell = cell.value
                if cell == None:
                    continue  # 데이터가 없으면 넘기기.
                cor_num, corrected_text = han_spell(str(cell))  # 셀의 데이터를 교정처리한다.
                if cor_num > 0:  # 수정이 있었다면 내용을 담는다.
                    wrong_text[cell] = corrected_text  # 잘못된 내용에 대한 정보를 추가.
        context['correct_info'] = wrong_text

    return render(request, 'utility/korean_spell/main.html', context)