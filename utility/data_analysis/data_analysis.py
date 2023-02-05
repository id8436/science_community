from django.shortcuts import render, get_object_or_404, redirect
import pandas as pd
from django.contrib.auth.decorators import login_required
from utility.models import DataObject
from django.contrib.auth.decorators import login_required
# 그림그리기용.
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import base64

@login_required()
def main(request):
    context = {}
    try:
        data_object = DataObject.objects.get(user=request.user)
        context['data_object'] = data_object
    except:
        pass
    return render(request, 'utility/data_analysis/main.html', context)

@login_required()
def upload_excel(request):
    context = {}
    if request.method == "POST":
        uploadedFile = request.FILES["uploadedFile"]  # post요청 안의 name속성으로 찾는다.
        df = pd.read_excel(uploadedFile)  # 요게 잘 받아지나??

        try:  # 객체가 없다면 에러를 반환하니까.
            data_object = DataObject.objects.get(user=request.user)  # 기존에 있었던 모델을 가져온다.
            data_object.delete()  # 기존 모델 지우기.
        except:
            pass
        df = df.dropna()
        data_object = DataObject.objects.create(user=request.user, info=str(df.describe()), contents=df.to_json())
        # json = df.to_json()
        #  # dj

    return redirect('utility:data_analysis_main')

def correlation(request):
    ## corr 자체를 DB에 저장해두었다 쓰려 했는데, 그러면 각종 계산에 어려움이 생긴다...
    context = {}
    data_object = DataObject.objects.get(user=request.user)
    # if data_object.correlation:
    #     correlation = data_object.correlation
    # else:
    df = pd.read_json(data_object.contents)
    correlation = df.corr()
    # data_object.correlation = correlation
    # data_object.save()
    context['correlation'] = correlation

    # 서버에서 폰트 종류 확인용으로 두었는데.. 되면 버리자.
    # import matplotlib.font_manager
    # font_list = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    # context['test'] = [matplotlib.font_manager.FontProperties(fname=font).get_name() for font in font_list]

    # 그림그리기 전 설정.
    plt.rc('font', family='NanumGothic')  # 한글을 지원하는 글꼴 지정.
    plt.rc('axes', unicode_minus=False)  # '-'값이 나오면 글자가 깨지는데, 이를 방지하기 위한 설정.
    # 그림그리기.
    plt.figure(figsize=(10, 5))
    sns.heatmap(df.corr(), linewidths=0.1, vmax=0.5, cmap='coolwarm', linecolor='white', annot=True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    context['graphic'] = graphic
    return render(request, 'utility/data_analysis/correlation.html', context)

def linearRegression(request):
    context = {}
    data_object = DataObject.objects.get(user=request.user)
    from sklearn.linear_model import LinearRegression
    # if data_object.correlation:
    #     correlation = data_object.correlation
    # else:
    df = pd.read_json(data_object.contents)
    x = df.iloc[:, :-1]  # 마지막 열 빼고 다 가져온다.
    y = df.iloc[:, -1]  # 마지막 열이 결과.
    model = LinearRegression()
    model.fit(x, y)

    context['intercept'] = model.intercept_  # y의 절편값
    context['coef'] = model.coef_  # 회귀계수(기울기)

    # 입력값 받을 폼 만들기.
    data_column = list(df.columns)[:-1]

    push_datas = {}  # 칼럼과 인풋정보를 담을 사전.
    if request.method == "POST":
        input_data = request.POST.getlist('input_data')
        input_data = list(map(float, input_data))  # 안의 데이터타입을 바꾸어줌.
        print(input_data)
        push = zip(data_column, input_data)
        for column, input in push:
            push_datas[column] = input

        # 회귀값 예상
        predict = model.predict([input_data])  # 2차원 배열을 받아 해당 행만큼 반환하는데, 여기선 1행만 받는다.
        context['predict'] = predict
    else:
        for column in data_column:
            push_datas[column] = ''
    context['push_datas'] = push_datas

    return render(request, 'utility/data_analysis/linearRegression.html', context)


def draw_graph_table(request):
    context = {}
    data_object = DataObject.objects.get(user=request.user)
    df = pd.read_json(data_object.contents)
    context['data_column_list'] = df.columns
    return render(request, 'utility/data_analysis/graph_table.html', context)

import plotly.express as px  # 그래프 그림.
from django.http import HttpResponse  # http 객체를 바로 내보내기 위해.
from plotly.offline import plot

def draw_graph(request):
    context = {}
    data_object = DataObject.objects.get(user=request.user)  # 기초데이터.
    df = pd.read_json(data_object.contents)
    if request.method == "POST":
        graph_type = request.POST.get('graph')
        x = request.POST.get('X')
        y = request.POST.get('Y')
        option = request.POST.get('option')
        if graph_type == 'line':
            df = df.sort_values(x, ascending=True)  # 줄을 세워야 제대로 된 선그래프가 나온다.
            fig = px.line(data_frame=df, x=x, y=y)
        elif graph_type == 'scatter':
            if request.POST.get('option2'):  # 옵션2가 선택되어 있다면...
                fig = px.scatter(data_frame=df, x=x, y=y, color=option, trendline="ols")
            else:
                fig = px.scatter(data_frame=df, x=x, y=y, color=option)
        elif graph_type == 'box':
            fig = px.box(data_frame=df, x=x, y=y)
        elif graph_type == 'bar':
            method = request.POST.get('method')
            df = df.groupby(x, as_index=False)  # 분류할 때 해당 열이 인덱스가 되지 않게끔.
            # 보통은 분류 후에 평균값이나 최댓값 등을 계산하여 통계화 한 후에 그래프를 만든다.
            df = df.agg(new=(y, method))  # 새로운열이름은 따옴표로 감싸지 않음에 유의, mean 등 다양한 방식이 가능하다.
            df = df.sort_values('new', ascending=True)  # 보통은 정렬하여 그래프를 그린다.
            fig = px.bar(data_frame=df, x=x, y='new', color=option)
        plot_div = plot(fig, output_type='div')

    return render(request, 'utility/data_analysis/graph.html', {'plot_div':plot_div})