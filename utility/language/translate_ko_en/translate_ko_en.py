from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from translate import Translator


def translate(request):
    context = {}
    if request.method == 'POST':
        korean = request.POST.get('korean')
        context['korean'] = korean
        translator = Translator(from_lang="ko", to_lang="en")
        translation = translator.translate(korean)
        context['translation'] = translation


    return render(request, 'utility/translate_ko_en/translate.html', context)