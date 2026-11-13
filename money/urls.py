from django.urls import path

from . import views


app_name = "money"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_setup, name="profile_setup"),
    path("budgets/new/", views.budget_create, name="budget_create"),
]

