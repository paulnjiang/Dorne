from django.http import HttpResponse,HttpResponseRedirect

from django.shortcuts import render, reverse

def index(request):
    return HttpResponseRedirect(reverse('user:users'))

def page_not_found(request):
    return render(request, 'error/404.html', {})

def page_error(request):
    return render(request, 'error/500.html', {})