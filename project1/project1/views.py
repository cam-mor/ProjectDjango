from django.http import HttpResponse
from django.shortcuts import render

def hi(request):
    return HttpResponse("Hello, World!")

# Your other views here...