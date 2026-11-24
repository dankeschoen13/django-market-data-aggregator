from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Stock, TrackedTicker

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


@api_view(['GET'])
def get_latest_metrics(request, ticker_symbol):

    latest_data = Stock.objects.get_latest_data(ticker_symbol)

    if not latest_data:
        return Response({
            "status": "error",
            "message": f"No available data for ticker {ticker_symbol}"
        }, status=404)

    return Response({
        "status": "success",
        "data": latest_data.to_dict()
    }, status=200)