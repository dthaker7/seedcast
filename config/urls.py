from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from money import views as money_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", money_views.landing, name="landing"),
    path("accounts/signup/", money_views.signup, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("money/", include("money.urls")),
]

