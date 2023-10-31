import openai
openai.api_key = "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"
# print(openai.Model.list())
# 조건
model = 'text-davinci-003'  # 선택할 수 있게! ex) gpt-3.5-turbo
max_tokens = 1700  # 입력에 1000정도 사용해서. 출력은 700 이하가 되게끔.
# messages = [{'role': 'system',
#              'content': role},
#             {'role': 'user',
#              'content': input_text}, ]

response = openai.Completion.create(
    engine=model,
    prompt='api 사용을 시도해보고 있어. 아무 말이나 해봐~',
    max_tokens=max_tokens
)
# 반
print(response)
print('답변')
print(response['choices'][0]['text'])  # 응답 중 답변만 추출한다.#answer = respond
response = response['choices'][0]['text']
response = response.replace('\n', '<br>')  # 탬플릿에서 줄바꿈이 인식되게끔.