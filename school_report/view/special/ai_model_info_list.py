price_list = {'gpt-3.5-turbo': 10, 'gpt-3.5-turbo-instruct':10,
              'gpt-4': 100, 'text-davinci-003': 10,'gpt-4-1106-preview':50,
              'gemini-pro':10, }

max_tocken_list = {'gpt-3.5-turbo': 4096, 'gpt-3.5-turbo-instruct':4096,
                   'gpt-4': 8192, 'text-davinci-003': 4096,
                   'gpt-4-1106-preview':128000,'gemini-pro':128000,  # 잼미니는 글자제한 없다고 함.
                   }

mechanism_list = {'gpt-3.5-turbo': 'ChatCompletion', 'gpt-3.5-turbo-instruct':'Completion',
                   'gpt-4': 'ChatCompletion', 'text-davinci-003': 'Completion',
                  'gpt-4-1106-preview':'ChatCompletion'}