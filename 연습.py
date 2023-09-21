import openai

openai.api_key = "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"
completion = openai.Completion()
# 조건
model = 'gpt-3'  # 선택할 수 있게!
max_tokens = 1000
messages = [{'role': 'system',
                'content':'teacher'},
            {'role':'assistant',
                'content':'API 사용법에 대한 설명이 더 필요한가요?'},
            {'role':'user',
             'content':'아무 말이나 해봐. respond에 대한 응답값을 보게.'},]

respond = completion.create(
    model = model,
    messages = messages,
)
print(respond)
#answer = respond