from django.contrib import admin
from .models import Stock, TrackedTicker

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticker',
        'trade_date',
        'close_price',
        'open_price',
        'high_price',
        'low_price',
        'volume',
        'rsi_14',
        'macd_line',
        'ema_50'
    )
    list_filter = ('trade_date', 'ticker')
    search_fields = ('ticker',)
    ordering = ('-trade_date',)

    def get_readonly_fields(self, request, obj=None):
        """
        Overrides get_readonly_fields method to make 'trade_date' and 'ticker'
        read-only on edits.
        """
        if obj:  # If obj exists, it's an edit
            return 'trade_date', 'ticker'
        return ()

@admin.register(TrackedTicker)
class TrackedTickerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticker',
        'is_active',
    )
    list_filter = ('is_active',)
    search_fields = ('ticker',)
    ordering = ('-is_active', 'ticker')

