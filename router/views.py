from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render

@api_view(['GET'])
def index(request):
    return Response({
        'status': 'Service is running!',
    }, status=200)
