from django.shortcuts import render, get_object_or_404, redirect, resolve_url
import numpy as np
from wordcloud import WordCloud

def main(request):
    context = {}
    return render(request, 'utility/wordcloud/main.html', context)

def create(request):
    context = {}
    if request.method == "POST":
        text = request.POST.get("text")
        base_image = request.FILES["base_image"]
        # print(base_image)
        # base_image = np.array(base_image)  # 이미지를 배열처리.
        # context['cloud_image'] = base_image
        # print(base_image.shape)

        wc = WordCloud(font_path='NanumGothic',  # 설치된 글꼴 지정. 속은 .ttf 경로 지정.
                       colormap='inferno')
        # img_cloud = wc.generate_from_frequencies(word_dict)  # 사전을 토대로 워드클라우드 생성.
        # plt.axis('off')  # 테두리선 없애기.
        # plt.imshow(img_cloud)  # 이미지 출력.
    # data_object = DataObject.objects.get(user=request.user)
    # df = pd.read_json(data_object.contents)
    # context['data_column_list'] = df.columns
    return render(request, 'utility/wordcloud/main.html', context)