from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def hello_api(request):
    return Response('ok')


# Create your views here.
