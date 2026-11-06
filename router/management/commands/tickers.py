"""
Management command for TrackedTicker operations.

Provides a unified CLI interface to seed, add, deactivate, remove, and list
monitored stock tickers within the database.

Usage:
    python manage.py tickers <action> [symbol]
"""

from django.core.management.base import BaseCommand, CommandError
from router.models import TrackedTicker

class Command(BaseCommand):
    """
    Django management command to manage tracked stock tickers.
    """
    help = 'Manage tracked stock tickers in the database'

    def add_arguments(self, parser):
        """
        Define the positional and optional arguments for the CLI command.

        Args:
            parser (ArgumentParser): The standard argparse parser instance.
        """
        parser.add_argument(
            'action',
            choices=['seed', 'add', 'deactivate', 'remove', 'list'],
            help='action to perform'
        )

        parser.add_argument(
            'symbol',
            nargs='?', # '?' means this argument is optional
            type=str,
            help='The ticker symbol (required for add, deactivate and remove)'
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
        symbol = kwargs.get('symbol')

        if action == 'seed':
            self._seed()
            return
        elif action == "list":
            self._list()
            return

        if not isinstance(symbol, str):
            raise CommandError(f'The "{action}" action requires a ticker symbol.')

        clean_symbol = symbol.upper().strip()

        if action == 'add':
            self._add_ticker(clean_symbol)
        elif action == 'deactivate':
            self._deactivate(clean_symbol)
        elif action == "remove":
            self._remove(clean_symbol)

    def _seed(self) -> None:
        """
        Populate the database with a default list of stock tickers.

        Uses set operations to efficiently deduplicate against existing database
        records before executing a bulk_create.
        """
        ticker_list = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL']

        # Creating a set to deduplicate:
        ticker_set = {ticker.upper().strip() for ticker in ticker_list}

        existing = set(
            TrackedTicker.objects.filter(ticker__in=ticker_set)
            .values_list('ticker', flat=True)
        )

        to_add = ticker_set - existing

        if len(to_add) == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No new tickers were added. All items already exist in the database."
                )
            )
            return

        # Creating TrackedTicker Objects
        instances = [TrackedTicker(ticker=sym) for sym in to_add]

        TrackedTicker.objects.bulk_create(instances, batch_size=500)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {len(to_add)} new ticker(s) to tracking."
            )
        )

    def _list(self) -> None:
        """
        Retrieve and print a list of all currently active tickers.
        """
        active_tickers = list(
            TrackedTicker.objects.active_tickers().values_list('ticker', flat=True)
        )

        if active_tickers:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Active tickers list: {active_tickers}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "There are no active tickers in the database"
                )
            )

    def _add_ticker(self, symbol: str) -> None:
        """
        Register a new ticker in the database or ignore if it already exists.

        Args:
            symbol (str): The stock ticker symbol to add.
        """
        ticker, created = TrackedTicker.objects.get_or_create(ticker=symbol)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Added {symbol} to tracking.'))
        else:
            self.stdout.write(self.style.WARNING(f'{symbol} is already being tracked.'))

    def _deactivate(self, symbol:str) -> None:
        """
        Soft-delete a ticker by setting its active status to False.

        Executes entirely at the database level via a bulk update query.

        Args:
            symbol (str): The stock ticker symbol to deactivate.
        """
        updated_count = TrackedTicker.objects.filter(ticker=symbol).update(is_active=False)

        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deactivated {symbol}.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Ticker symbol: {symbol} is not found in the database.')
            )

    def _remove(self, symbol: str) -> None:
        """
        Hard-delete a ticker record from the database.

        Args:
            symbol (str): The stock ticker symbol to permanently remove.
        """
        count, _ = TrackedTicker.objects.filter(ticker=symbol).delete()

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully removed {symbol}.'))
        else:
            self.stdout.write(self.style.ERROR(f'Ticker {symbol} was not found in the database.'))

