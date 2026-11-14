from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Forecast, MarketAsset

DISCLAIMER = "Educational paper-money simulation only. Not investment advice."


def _filtered_assets(request):
    assets = MarketAsset.objects.filter(is_active=True).prefetch_related("forecasts", "prices")
    query = request.GET.get("q", "").strip()
    asset_type = request.GET.get("type", "").strip()
    if query:
        assets = assets.filter(Q(ticker__icontains=query) | Q(name__icontains=query))
    if asset_type in MarketAsset.AssetType.values:
        assets = assets.filter(asset_type=asset_type)
    else:
        asset_type = ""
    return assets, query, asset_type


@require_GET
def explorer(request):
    """Cast Explorer: browse curated assets and their latest saved forecast."""
    assets, query, asset_type = _filtered_assets(request)
    return render(
        request,
        "markets/explorer.html",
        {
            "assets": assets,
            "query": query,
            "asset_type": asset_type,
            "asset_types": MarketAsset.AssetType.choices,
            "disclaimer": DISCLAIMER,
        },
    )


@require_GET
def asset_detail(request, ticker):
    asset = get_object_or_404(MarketAsset, ticker=ticker.upper(), is_active=True)
    return render(
        request,
        "markets/asset_detail.html",
        {
            "asset": asset,
            "forecast": asset.latest_forecast,
            "prices": asset.prices.all()[:30],
            "disclaimer": DISCLAIMER,
        },
    )


@require_GET
def api_assets(request):
    """JSON list of curated assets (respects the same ?q= and ?type= filters)."""
    assets, _, _ = _filtered_assets(request)
    results = []
    for asset in assets:
        forecast = asset.latest_forecast
        price = asset.latest_price
        results.append(
            {
                "ticker": asset.ticker,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "sector": asset.sector,
                "latest_close": None if price is None else float(price.close),
                "latest_close_date": None if price is None else price.date.isoformat(),
                "has_forecast": bool(forecast and forecast.is_computed),
            }
        )
    return JsonResponse({"count": len(results), "results": results, "disclaimer": DISCLAIMER})


@require_GET
def api_forecast(request, ticker):
    """Latest saved forecast for one ticker, in the TEAM_SETUP.md contract shape.

    - Unknown ticker -> 404 with an error message.
    - Known ticker without a saved forecast -> 200 with every prediction field
      null and status "unavailable" (never a zero or invented number).
    """
    asset = MarketAsset.objects.filter(ticker=ticker.upper(), is_active=True).first()
    if asset is None:
        return JsonResponse({"error": f"Unknown ticker '{ticker.upper()}'."}, status=404)

    forecast = asset.latest_forecast
    if forecast is None:
        payload = {
            "ticker": asset.ticker,
            "as_of_date": None,
            "horizon_trading_days": None,
            "expected_return": None,
            "p10_return": None,
            "p90_return": None,
            "probability_positive": None,
            "model_version": None,
            "data_source": None,
            "status": "unavailable",
            "is_stale": None,
        }
    else:
        payload = forecast.to_contract_dict()
        stale = forecast.is_stale()
        payload["is_stale"] = stale
        if not forecast.is_computed:
            payload["status"] = "unavailable"
        else:
            payload["status"] = "stale" if stale else "ok"
    payload["units"] = "Returns are decimals: 0.01 means 1%."
    payload["disclaimer"] = DISCLAIMER
    return JsonResponse(payload)
