from django.db.models import UniqueConstraint
from django.db import models, DatabaseError, transaction
from decimal import Decimal
import pandas as pd
import datetime
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class StockManager(models.Manager):

    def _prepare_data_dict(self, df: pd.DataFrame) -> dict:
        """
        Converts the latest DataFrame row into a clean dictionary
        matching the target model's concrete fields.
        """
        if df.empty:
            raise ValueError("DataFrame is empty.")

        # Dynamically retrieve valid field names for the associated model
        # noinspection PyProtectedMember
        valid_fields = {f.name for f in self.model._meta.concrete_fields}

        # Extract latest row as a dictionary
        row = df.iloc[-1].to_dict()
        entry_dict = {}

        for col, val in row.items():
            if col not in valid_fields:
                continue

            # Convert Pandas/NumPy missing values to Python None
            if pd.isna(val):
                entry_dict[col] = None
                continue

            # Convert Pandas Timestamps to datetime.date / datetime.datetime
            if isinstance(val, pd.Timestamp):
                val = val.date()

            # Convert NumPy scalar types (e.g. np.float64, np.int64) to native Python
            elif hasattr(val, 'item'):
                val = val.item()

            entry_dict[col] = val

        return entry_dict

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

    def load_data(self, df: pd.DataFrame) -> None:
        """
        Loads the latest market data entry from a DataFrame into PostgreSQL.
        """

        entry_dict = self._prepare_data_dict(df)

        unique_fields = ['ticker', 'trade_date']
        update_fields = [k for k in entry_dict.keys() if k not in unique_fields]

        try:
            with transaction.atomic():
                self.bulk_create(
                    [self.model(**entry_dict)],
                    update_conflicts=True,
                    unique_fields=unique_fields,
                    update_fields=update_fields,
                )
        except DatabaseError as e:
            ticker = entry_dict.get('ticker', 'UNKNOWN')
            logger.error(f"Database transaction failed for {ticker}: {e}")
            raise ValueError(f"Failed to load data for {ticker}: {e}") from e

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

