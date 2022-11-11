import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity  # 유사도 검사


# 채팅 기초 설정.
embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
dialog_df = pd.read_csv('utility/mental_health_chatbot/wellness_dataset.csv')
def chatbot(message):
    embedding = embedding_model.encode(message)
    dialog_df['embedding'] = dialog_df['embedding'].apply(json.loads)  # json을 적절한 형태로 받아들이기.
    dialog_df['distance'] = dialog_df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())
    answer = dialog_df.loc[dialog_df['distance'].idxmax()]
    answer = answer['챗봇']  # 대답행(row) 중에서 챗봇의 응답만 담는다.
    return answer

answer = chatbot('하이')
print(answer)