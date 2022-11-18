from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from translate import Translator


def translate(request):
    context = {}
    language_list ={'ko':'한국어', 'en':'영어'}
    if request.method == 'POST':
        # 사용하는 언어정보.
        original_language = request.POST.getlist('original_language')[0]
        translated_language = request.POST.getlist('translated_language')[0]
        context['original_language'] = original_language
        context['translated_language'] = translated_language
        # 번역기.
        translator = Translator(from_lang=original_language, to_lang=translated_language)
        original_text = request.POST.get('original_text')
        context['original_text'] = original_text
        translated_text = translator.translate(original_text)
        context['translated_text'] = translated_text

    context['language_list'] = language_list
    print(context)

    return render(request, 'utility/translate_ko_en/translate.html', context)