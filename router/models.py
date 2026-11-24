from django.db.models import UniqueConstraint
from django.db import models
from decimal import Decimal
import datetime

# Create your models here.

class StockManager(models.Manager):

    def get_latest_data(self, ticker_symbol: str):
        """
        Pulls the latest market data of the specified ticker
        from the database

        Args:
            ticker_symbol: the ticker of the stock data need to be pulled

        Returns:
            Stock | None: A Stock scalar or None
        """
        return self.filter(ticker=ticker_symbol).first()

class Stock(models.Model):

    # Required cols
    ticker = models.CharField(max_length=15)
    trade_date = models.DateField()
    close_price = models.FloatField()

    # Non Required
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)

    # Computed
    rsi_14 = models.FloatField(null=True, blank=True)
    macd_line = models.FloatField(null=True, blank=True)
    ema_50 = models.FloatField(null=True, blank=True)

    objects = StockManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['ticker', 'trade_date'],
                name='unique_client_order_timestamp'
            )
        ]
        ordering = ['-trade_date']

    def to_dict(self):
        data = {}
        excluded_cols = ['id']

        for column in self._meta.fields:

            value = getattr(self, column.name)

            if column.name in excluded_cols:
                continue

            # Dates and Datetimes => ISO 8601 strings
            if isinstance(value, (datetime.date, datetime.datetime)):
                data[column.name] = value.isoformat()

            # Decimals => floats
            elif isinstance(value, Decimal):
                data[column.name] = float(value)

            else:
                data[column.name] = value

        return data


class TrackedTickerManager(models.Manager):

    def active_tickers(self):
        """
        Returns query set filtering active tickers
        """
        return self.filter(is_active=True)

class TrackedTicker(models.Model):
    ticker = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True, db_default=True)

    objects = TrackedTickerManager()

