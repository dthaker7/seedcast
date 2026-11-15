from django.contrib import admin

from .models import Forecast, MarketAsset, PriceBar


@admin.register(MarketAsset)
class MarketAssetAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "asset_type", "sector", "is_active")
    list_filter = ("asset_type", "sector", "is_active")
    search_fields = ("ticker", "name")


@admin.register(PriceBar)
class PriceBarAdmin(admin.ModelAdmin):
    list_display = ("asset", "date", "close", "volume", "source")
    list_filter = ("asset",)


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("asset", "as_of_date", "horizon_trading_days", "expected_return", "model_version")
    list_filter = ("asset", "model_version")
