from django.shortcuts import render


def indexView(request):

    context = {
        'title': 'Sparklay'
    }

    return render(request, 'index.html', context)

def mainView(request):

    context = {
        'title': 'Sparklay'
    }

    return render(request, 'sparklay/main.html', context)
