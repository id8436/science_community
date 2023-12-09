price_list = {'gpt-3.5-turbo': 10, 'gpt-3.5-turbo-instruct':10,
              'gpt-4': 100, 'text-davinci-003': 10,'gpt-4-1106-preview':50,}

max_tocken_list = {'gpt-3.5-turbo': 4096, 'gpt-3.5-turbo-instruct':4096,
                   'gpt-4': 8192, 'text-davinci-003': 4096,
                   'gpt-4-1106-preview':128000,}

mechanism_list = {'gpt-3.5-turbo': 'ChatCompletion', 'gpt-3.5-turbo-instruct':'Completion',
                   'gpt-4': 'ChatCompletion', 'text-davinci-003': 'Completion',
                  'gpt-4-1106-preview':'ChatCompletion'}