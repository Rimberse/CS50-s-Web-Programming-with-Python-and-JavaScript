from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# request represents an HTTP request, which can accessed to see request properties
# render function renders an html file contained in templates/hello folder
def index(request):
    return render(request, 'hello/index.html')

def kerim(request):
    return HttpResponse('Hello, Kerim!')

def david(request):
    return HttpResponse('Hello, David!')

# 3rd argument if a context
def greet(request, name):
    return render(request, 'hello/greet.html', {
        'name': name.capitalize()
    })