import os

from wordcloud import WordCloud
import konlpy

hannanum = konlpy.tag.Hannanum()
text = '''속에 감췄드니 이튿날 아침 빗자루가 없다고 어머니가 야단이지요.
People also search for
R wordcloud2
R wordcloud 오류
r 워드클라우드 만들기
R wordcloud 예제
r 워드클라우드 txt
r 워드클라우드 모양
ta1000.tistory.com › ...
Feb 12, 2020 — 미국 질병관리국이 신종 코로나 바이러스에 마스크 필요 없다고 발표한 ... from wordcloud import WordCloud import matplotlib.pyplot as plt ...
파이썬을 이용한 영화 리뷰 분석 (웹 크롤링 & 자연어 처리)'''
nouns = hannanum.nouns(text)

import pandas as pd

df = pd.DataFrame({'word': nouns})  # 리스트로 데이터프레임을 만들고,

# 단어 빈도 세기
df = df.groupby('word', as_index=False) \
        .agg(count = ('word', 'count')) \
        .sort_values('count', ascending=False)  # 내림차순 정렬
print(df)

wc = WordCloud(font_path='NanumGothic',  # 설치된 글꼴 지정. 속은 .ttf 경로 지정.
                       colormap='inferno')
img_cloud = wc.generate_from_frequencies(word_dict)  # 사전을 토대로 워드클라우드 생성.
plt.imshow(img_cloud)