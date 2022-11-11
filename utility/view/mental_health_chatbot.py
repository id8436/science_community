from django.shortcuts import render, get_object_or_404, redirect, resolve_url

def chatroom(request):
    context = {}
    #  폼을 통해 들어온 데이터를 받는다.

    return render(request, 'utility/mental_health_chatbot/chatroom.html', context)