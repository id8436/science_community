from django.http import HttpResponse
import pandas as pd
import re
'''dataframe과 관련한 기능들을 모아둔 문서.'''



# def df_to_dic(df):

def df_to_excel_download(df, filename='지난지나니 다운'):
    '''df를 엑셀로 다운.'''
    df = df.applymap(clean_data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    from django.utils.encoding import escape_uri_path  # 파일명을 '다운로드'가 아닌 지정한 형태로 가져가기 위해 필요한 것.
    filename = f"{filename}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(filename)}"'
    df.to_excel(response, index=False)
    return response
def clean_data(value):
    """유효하지 않은 문자를 제거하는 함수."""
    if isinstance(value, str):
        return re.sub(r'[\x00-\x1F\x7F]', '', value)
    return value
def upload_to_df(excel_file):
    '''excel_file = request.FILES["uploadedFile"] 형태로 받는다.'''
    # 혹시 나중에 파일명 등 조작할 경우를 대비해 모듈화 해놓는 게 좋을 듯하여 간단하지만 작성해 둔다.
    df = pd.read_excel(excel_file)
    return df