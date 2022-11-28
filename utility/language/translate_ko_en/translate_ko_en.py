from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from translate import Translator
from googletrans import Translator as googleTrans

def translate(request):
    context = {}
    language_list ={'none':'지정안함(자동탐지)', 'ko':'한국어', 'ru':'러시아어', 'en':'영어'}
    if request.method == 'POST':
        # 사용하는 언어정보.
        original_language = request.POST.getlist('original_language')[0]
        translated_language = request.POST.getlist('translated_language')[0]
        context['original_language'] = original_language
        context['translated_language'] = translated_language
        # 번역기.
        original_text = request.POST.get('original_text')
        context['original_text'] = original_text
        if original_language == 'none':  # 일단 언어탐지부터.
            googletranslator = googleTrans()
            detection = googletranslator.detect(original_text)
            original_language = detection.lang
        # 번역.
        translator = Translator(from_lang=original_language, to_lang=translated_language)
        translated_text = translator.translate(original_text)
        context['translated_text'] = translated_text
        # 영어 검증.
        translator = Translator(from_lang=original_language, to_lang='en')
        verification_en = translator.translate(original_text)
        context['verification_en'] = verification_en
        # 영어를 다시 번역.
        translator = Translator(from_lang='en', to_lang=translated_language)
        verification_again = translator.translate(verification_en)
        context['verification_again'] = verification_again

    context['language_list'] = language_list

    return render(request, 'utility/translate_ko_en/translate.html', context)