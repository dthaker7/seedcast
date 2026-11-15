import tempfile
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Forecast, MarketAsset, PriceBar


def make_asset(ticker="SPY", name="SPDR S&P 500 ETF Trust", asset_type="etf", **extra):
    return MarketAsset.objects.create(ticker=ticker, name=name, asset_type=asset_type, **extra)


class MarketModelTests(TestCase):
    def test_ticker_is_normalized_to_uppercase(self):
        asset = make_asset(ticker=" aapl ", name="Apple Inc.", asset_type="stock")
        self.assertEqual(asset.ticker, "AAPL")

    def test_one_price_per_asset_per_day(self):
        asset = make_asset()
        PriceBar.objects.create(asset=asset, date=date(2026, 11, 12), close=Decimal("600.00"))
        with self.assertRaises(IntegrityError):
            PriceBar.objects.create(asset=asset, date=date(2026, 11, 12), close=Decimal("601.00"))

    def test_forecast_p10_cannot_exceed_p90(self):
        asset = make_asset()
        with self.assertRaises(IntegrityError):
            Forecast.objects.create(
                asset=asset,
                as_of_date=date(2026, 11, 12),
                p10_return=Decimal("0.05"),
                p90_return=Decimal("-0.05"),
            )

    def test_latest_forecast_and_contract_shape(self):
        asset = make_asset()
        Forecast.objects.create(asset=asset, as_of_date=date(2026, 11, 1), model_version="v0")
        newest = Forecast.objects.create(
            asset=asset,
            as_of_date=date(2026, 11, 12),
            expected_return=Decimal("0.012"),
            p10_return=Decimal("-0.03"),
            p90_return=Decimal("0.05"),
            probability_positive=Decimal("0.58"),
            model_version="v1",
            data_source="test",
        )
        self.assertEqual(asset.latest_forecast, newest)
        self.assertEqual(
            set(newest.to_contract_dict()),
            {
                "ticker", "as_of_date", "horizon_trading_days", "expected_return", "p10_return",
                "p90_return", "probability_positive", "model_version", "data_source",
            },
        )

    def test_stale_forecast_detection(self):
        asset = make_asset()
        forecast = Forecast.objects.create(asset=asset, as_of_date=date(2026, 11, 1))
        self.assertFalse(forecast.is_stale(today=date(2026, 11, 8)))
        self.assertTrue(forecast.is_stale(today=date(2026, 11, 9)))


class DemoFixtureTests(TestCase):
    def test_demo_assets_fixture_loads_curated_assets(self):
        call_command("loaddata", "demo_assets", verbosity=0)
        self.assertEqual(MarketAsset.objects.count(), 10)
        self.assertTrue(MarketAsset.objects.filter(ticker="SPY", asset_type="etf").exists())
        # The fixture holds assets only: no invented prices or forecasts.
        self.assertFalse(PriceBar.objects.exists())
        self.assertFalse(Forecast.objects.exists())


class CastExplorerViewTests(TestCase):
    def setUp(self):
        self.spy = make_asset()
        self.aapl = make_asset(ticker="AAPL", name="Apple Inc.", asset_type="stock", sector="Technology")
        make_asset(ticker="OLD", name="Delisted Example", asset_type="stock", is_active=False)

    def test_explorer_lists_active_assets_only(self):
        response = self.client.get(reverse("markets:explorer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SPY")
        self.assertContains(response, "AAPL")
        self.assertNotContains(response, "Delisted Example")

    def test_search_by_name_and_filter_by_type(self):
        response = self.client.get(reverse("markets:explorer"), {"q": "apple"})
        self.assertEqual(list(response.context["assets"]), [self.aapl])
        response = self.client.get(reverse("markets:explorer"), {"type": "etf"})
        self.assertEqual(list(response.context["assets"]), [self.spy])

    def test_invalid_type_filter_is_ignored(self):
        response = self.client.get(reverse("markets:explorer"), {"type": "crypto"})
        self.assertEqual(len(response.context["assets"]), 2)

    def test_no_matches_shows_empty_state(self):
        response = self.client.get(reverse("markets:explorer"), {"q": "zzzz"})
        self.assertContains(response, "No assets match")

    def test_missing_forecast_is_shown_as_not_computed(self):
        response = self.client.get(reverse("markets:explorer"))
        self.assertContains(response, "Forecast not computed yet")
        self.assertNotContains(response, "0.0%")

    def test_saved_forecast_is_shown_as_percent(self):
        Forecast.objects.create(
            asset=self.spy,
            as_of_date=timezone.localdate(),
            expected_return=Decimal("0.0125"),
            p10_return=Decimal("-0.0300"),
            p90_return=Decimal("0.0500"),
            probability_positive=Decimal("0.6"),
            model_version="test",
        )
        response = self.client.get(reverse("markets:asset_detail", args=["spy"]))
        self.assertContains(response, "1.3%")
        self.assertContains(response, "-3.0% to 5.0%")
        self.assertContains(response, "60%")

    def test_unknown_ticker_detail_returns_404(self):
        response = self.client.get(reverse("markets:asset_detail", args=["NOPE"]))
        self.assertEqual(response.status_code, 404)


class MarketApiTests(TestCase):
    def setUp(self):
        self.spy = make_asset()
        PriceBar.objects.create(asset=self.spy, date=date(2026, 11, 12), close=Decimal("601.25"), source="test")

    def test_assets_endpoint_returns_json_list(self):
        response = self.client.get(reverse("markets:api_assets"))
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["ticker"], "SPY")
        self.assertEqual(data["results"][0]["latest_close"], 601.25)
        self.assertFalse(data["results"][0]["has_forecast"])

    def test_forecast_endpoint_unknown_ticker_is_404(self):
        response = self.client.get(reverse("markets:api_forecast", args=["NOPE"]))
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_forecast_endpoint_without_forecast_returns_nulls_not_zeros(self):
        data = self.client.get(reverse("markets:api_forecast", args=["spy"])).json()
        self.assertEqual(data["status"], "unavailable")
        for key in ("expected_return", "p10_return", "p90_return", "probability_positive"):
            self.assertIsNone(data[key], key)

    def test_forecast_endpoint_returns_saved_forecast(self):
        Forecast.objects.create(
            asset=self.spy,
            as_of_date=timezone.localdate(),
            expected_return=Decimal("0.01"),
            p10_return=Decimal("-0.02"),
            p90_return=Decimal("0.04"),
            probability_positive=Decimal("0.57"),
            model_version="v1",
            data_source="frozen-sample",
        )
        data = self.client.get(reverse("markets:api_forecast", args=["SPY"])).json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["expected_return"], 0.01)
        self.assertEqual(data["model_version"], "v1")
        self.assertFalse(data["is_stale"])

    def test_forecast_endpoint_flags_stale_forecast(self):
        Forecast.objects.create(
            asset=self.spy,
            as_of_date=timezone.localdate() - timedelta(days=30),
            expected_return=Decimal("0.01"),
        )
        data = self.client.get(reverse("markets:api_forecast", args=["SPY"])).json()
        self.assertEqual(data["status"], "stale")
        self.assertTrue(data["is_stale"])

    def test_api_rejects_post(self):
        response = self.client.post(reverse("markets:api_assets"))
        self.assertEqual(response.status_code, 405)


class ImportPricesCommandTests(TestCase):
    def test_imports_valid_rows_and_skips_bad_ones(self):
        make_asset()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prices.csv"
            path.write_text(
                "ticker,date,close,volume\n"
                "spy,2026-11-11,600.10,1000\n"
                "SPY,2026-11-12,601.25,\n"
                "XXXX,2026-11-12,10.00,5\n"
                "SPY,not-a-date,1.00,5\n"
                "SPY,2026-11-13,-4,5\n",
                encoding="utf-8",
            )
            out, err = StringIO(), StringIO()
            call_command("import_prices", str(path), "--source", "unit-test", stdout=out, stderr=err)
        self.assertEqual(PriceBar.objects.count(), 2)
        self.assertIn("2 created, 0 updated, 3 skipped", out.getvalue())
        self.assertIn("unknown ticker", err.getvalue())
