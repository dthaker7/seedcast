from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class MarketAsset(models.Model):
    """A ticker that Seedcast can show in Cast Explorer."""

    class AssetType(models.TextChoices):
        ETF = "etf", "ETF / index fund"
        STOCK = "stock", "Individual stock"

    ticker = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=10, choices=AssetType.choices)
    sector = models.CharField(max_length=60, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ticker"]

    def save(self, *args, **kwargs):
        self.ticker = self.ticker.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticker} ({self.name})"

    @property
    def latest_price(self):
        return self.prices.order_by("-date").first()

    @property
    def latest_forecast(self):
        return self.forecasts.order_by("-as_of_date", "-created_at").first()


class PriceBar(models.Model):
    """One daily closing price, loaded from a cached/frozen CSV (never live per request)."""

    asset = models.ForeignKey(MarketAsset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField()
    close = models.DecimalField(
        max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal("0.0001"))]
    )
    volume = models.BigIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    source = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["asset", "date"], name="unique_price_per_asset_day")
        ]

    def __str__(self):
        return f"{self.asset.ticker} {self.date}: {self.close}"


class Forecast(models.Model):
    """A saved model forecast, matching the TEAM_SETUP.md planning contract.

    Returns are decimals (0.01 == 1%). ``None`` means "not computed yet";
    missing predictions are never replaced with invented values. The
    intelligence app (Dhruv) writes rows here; markets only reads them.
    """

    asset = models.ForeignKey(MarketAsset, on_delete=models.CASCADE, related_name="forecasts")
    as_of_date = models.DateField()
    horizon_trading_days = models.PositiveSmallIntegerField(default=21)
    expected_return = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    p10_return = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    p90_return = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    probability_positive = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
    )
    model_version = models.CharField(max_length=60, blank=True)
    data_source = models.CharField(max_length=60, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STALE_AFTER_DAYS = 7

    class Meta:
        ordering = ["-as_of_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "as_of_date", "horizon_trading_days", "model_version"],
                name="unique_forecast_per_asset_date_horizon_model",
            ),
            models.CheckConstraint(
                condition=models.Q(p10_return__isnull=True)
                | models.Q(p90_return__isnull=True)
                | models.Q(p10_return__lte=models.F("p90_return")),
                name="forecast_p10_not_above_p90",
            ),
        ]

    def __str__(self):
        return f"{self.asset.ticker} forecast as of {self.as_of_date}"

    @property
    def is_computed(self):
        return self.expected_return is not None

    def is_stale(self, today=None):
        today = today or timezone.localdate()
        return (today - self.as_of_date).days > self.STALE_AFTER_DAYS

    def to_contract_dict(self):
        def num(value):
            return None if value is None else float(value)

        return {
            "ticker": self.asset.ticker,
            "as_of_date": self.as_of_date.isoformat(),
            "horizon_trading_days": self.horizon_trading_days,
            "expected_return": num(self.expected_return),
            "p10_return": num(self.p10_return),
            "p90_return": num(self.p90_return),
            "probability_positive": num(self.probability_positive),
            "model_version": self.model_version or None,
            "data_source": self.data_source or None,
        }
