from django.urls import path

from . import views


app_name = "markets"

urlpatterns = [
    path("", views.explorer, name="explorer"),
    path("api/assets/", views.api_assets, name="api_assets"),
    path("api/forecasts/<str:ticker>/", views.api_forecast, name="api_forecast"),
    path("<str:ticker>/", views.asset_detail, name="asset_detail"),
]
