"""Load cached daily closing prices from a CSV file.

Expected header: ticker,date,close[,volume]
Example: python manage.py import_prices data/prices.csv --source yfinance-cache

Prices are imported offline from a frozen file, never fetched inside a web
request. Unknown tickers and malformed rows are reported and skipped.
"""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from markets.models import MarketAsset, PriceBar


class Command(BaseCommand):
    help = "Import cached daily closing prices from a CSV file (ticker,date,close[,volume])."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--source", default="csv-import")

    def handle(self, *args, csv_path, source, **options):
        path = Path(csv_path)
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        assets = {asset.ticker: asset for asset in MarketAsset.objects.all()}
        created = updated = skipped = 0
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = {"ticker", "date", "close"} - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV is missing columns: {', '.join(sorted(missing))}")
            for line_number, row in enumerate(reader, start=2):
                ticker = (row.get("ticker") or "").strip().upper()
                asset = assets.get(ticker)
                try:
                    if asset is None:
                        raise ValueError(f"unknown ticker {ticker!r}")
                    day = date.fromisoformat(row["date"].strip())
                    close = Decimal(row["close"].strip())
                    if close <= 0:
                        raise ValueError("close must be positive")
                    volume_raw = (row.get("volume") or "").strip()
                    volume = int(float(volume_raw)) if volume_raw else None
                    if volume is not None and volume < 0:
                        raise ValueError("volume must not be negative")
                except (ValueError, InvalidOperation) as error:
                    skipped += 1
                    self.stderr.write(f"Line {line_number}: skipped ({error})")
                    continue
                _, was_created = PriceBar.objects.update_or_create(
                    asset=asset,
                    date=day,
                    defaults={"close": close, "volume": volume, "source": source},
                )
                created += was_created
                updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(f"Prices imported: {created} created, {updated} updated, {skipped} skipped.")
        )
