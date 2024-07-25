# 24.07.24 기준 gpt-4가 1M에 평균 45달러임. 원화로 하면 대충 0.007원.
# 현재 gpt 모델은 문자열에서 gpt로 시작되는 것만으로 따로 다루고 있으니, gpt로 시작되지 않는 모델에 대해선 tasks.py 안의 작동 살피기.
price_list = {'gpt-3.5-turbo': 1, 'gpt-3.5-turbo-instruct':0.25,
              'gpt-4': 10, 'gpt-4o':20, 'gpt-4o-mini':0.25, 'gpt-4-turbo':40,
              'gemini-pro':10,
              # 없앤 것.
            'text-davinci-003': 10, 'gpt-4-1106-preview':5,
              }

max_tocken_list = {'gpt-3.5-turbo': 16385, 'gpt-3.5-turbo-instruct':4096,
                   'gpt-4': 8192, 'text-davinci-003': 4096, 'gpt-4o':128000, 'gpt-4o-mini':128000, 'gpt-4-turbo':128000,
                   'gpt-4-1106-preview':128000,'gemini-pro':128000,  # 잼미니는 글자제한 없다고 함.
                   }

mechanism_list = {'gpt-3.5-turbo': 'ChatCompletion', 'gpt-3.5-turbo-instruct':'Completion',
                   'gpt-4': 'ChatCompletion', 'text-davinci-003': 'Completion',
                  'gpt-4-1106-preview':'ChatCompletion',
        'gpt-4o':'ChatCompletion', 'gpt-4o-mini':'ChatCompletion', 'gpt-4-turbo':'ChatCompletion',
                  'gemini-pro':'google'}