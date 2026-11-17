"""Load the frozen AAPL history and save a reproducible model forecast."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ai_feasibility.experiment import load_frozen_market_data, predict_latest_return
from markets.models import Forecast, MarketAsset, PriceBar


DEFAULT_DATASET = Path("data/aapl_daily_2015_2017.csv")
DATA_SOURCE = "plotly-frozen-aapl"


class Command(BaseCommand):
    help = "Load frozen AAPL prices, run the real model, and save a demo forecast."

    def add_arguments(self, parser):
        parser.add_argument("--data", type=Path, default=DEFAULT_DATASET)

    @transaction.atomic
    def handle(self, *args, data, **options):
        if not data.exists():
            raise CommandError(f"File not found: {data}")

        call_command("loaddata", "demo_assets", verbosity=0)
        asset = MarketAsset.objects.get(ticker="AAPL")
        market_data = load_frozen_market_data(data)
        price_rows = [
            PriceBar(
                asset=asset,
                date=row.Date.date(),
                close=Decimal(str(row.adjusted_close)),
                volume=int(row.volume),
                source=DATA_SOURCE,
            )
            for row in market_data.itertuples(index=False)
        ]
        PriceBar.objects.bulk_create(
            price_rows,
            update_conflicts=True,
            update_fields=["close", "volume", "source"],
            unique_fields=["asset", "date"],
        )

        prediction = predict_latest_return(data)
        forecast, _ = Forecast.objects.update_or_create(
            asset=asset,
            as_of_date=date.fromisoformat(prediction.as_of_date),
            horizon_trading_days=prediction.horizon_trading_days,
            model_version=prediction.model_version,
            defaults={
                "expected_return": Decimal(str(prediction.expected_return)),
                "p10_return": Decimal(str(prediction.p10_return)),
                "p90_return": Decimal(str(prediction.p90_return)),
                "probability_positive": Decimal(str(prediction.probability_positive)),
                "data_source": DATA_SOURCE,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo ready: {len(price_rows)} AAPL prices and forecast {forecast.pk} "
                f"({prediction.expected_return:.2%} expected return)."
            )
        )
