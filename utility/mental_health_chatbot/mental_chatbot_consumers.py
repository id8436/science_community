import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity  # 유사도 검사


# 채팅 기초 설정.
embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
dialog_df = pd.read_csv('utility/mental_health_chatbot/wellness_dataset.csv')
dialog_df['embedding'] = dialog_df['embedding'].apply(json.loads)  # json을 적절한 형태로 받아들이기.
def chatbot(message):
    embedding = embedding_model.encode(message)
    dialog_df['distance'] = dialog_df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())
    answer = dialog_df.loc[dialog_df['distance'].idxmax()]
    answer = answer['챗봇']  # 대답행(row) 중에서 챗봇의 응답만 담는다.
    return answer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "mental_health_chatbot"

        # "room" 그룹에 가입
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # "room" 그룹에서 탈퇴
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    # 웹소켓 으로 부터 메시지 수신
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # "room" 그룹에 메시지 전송
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        # 챗봇 응답.
        answer = chatbot(message)
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': answer
            }
        )


    # "room" 그룹에서 메시지 전송
    def chat_message(self, event):
        message = event['message']

        # 웹 소켓으로 메시지 전송
        self.send(text_data=json.dumps({
            'message': message
        }))