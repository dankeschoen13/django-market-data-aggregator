from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TrackedTicker
from django.shortcuts import render

@api_view(['GET'])
def index(request):
    return Response({
        'status': 'Service is running!',
    }, status=200)


@api_view(['GET'])
def get_available_tickers(request):
    active_tickers = list(TrackedTicker.objects.active_tickers())

    if not active_tickers:
        return Response({
            "status": "error",
            "message": "No active tickers found in the database."
        }, status=404)

    return Response({
        "status": "success",
        "data": [stock.ticker for stock in active_tickers],
        "meta": {"count": len(active_tickers)}
    }, status=200)