from django.core.management.base import BaseCommand, CommandError
from router.models import Stock, TrackedTicker
from router.services import fetch_latest_stock_data
from django.conf import settings
import pandas as pd

class Command(BaseCommand):

    help = 'Manage stock data in the database'

    def add_arguments(self, parser):
        """
        Define the positional and optional arguments for the CLI command.

        Args:
            parser (ArgumentParser): The standard argparse parser instance.
        """
        parser.add_argument(
            'action',
            choices=['get'],
            help='action to perform'
        )

    def handle(self, *args, **kwargs) -> None:
        """
        Execute the command, validate inputs, and route to the appropriate helper method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments containing 'action' and 'symbol'.

        Raises:
            CommandError: If an action that requires a symbol is called without one.
        """
        action = kwargs['action']

        if action == 'get':
            self._get_stock_data()

    def _get_stock_data(self):

        api_key = settings.FMP_KEY
        if not api_key:
            self.stdout.write(
                self.style.ERROR("Critical Error: FMP_KEY is missing from app configuration.")
            )
            return

        tickers = list(
            TrackedTicker.objects.active_tickers().values_list('ticker', flat=True)
        )
        if not tickers:
            self.stdout.write(
                self.style.WARNING("No active tickers found in the database to update.")
            )
            return

        self.stdout.write(f"Starting market data update for {len(tickers)} tickers...")

        for symbol in tickers:
            self.stdout.write(f"Fetching data for {symbol}...")

            try:
                # a. Extract
                stock_data = fetch_latest_stock_data(symbol, api_key)

                # b. Validate
                if isinstance(stock_data, pd.DataFrame):

                    # c. Load
                    Stock.objects.load_data(stock_data)
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✔ Success! {symbol} data updated.")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  ✖ Failed to extract valid data for {symbol}.")
                    )

            except Exception as e:
                # d. Catch unexpected extraction network errors or database SQLAlchemyErrors
                self.stdout.write(
                    self.style.ERROR(f"  ! Critical error processing {symbol}: {e}")
                )