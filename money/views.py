from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import FinancialProfileForm, MonthlyBudgetForm, SignUpForm
from .models import FinancialProfile


def landing(request):
    if request.user.is_authenticated:
        return redirect("money:dashboard")
    return render(request, "money/landing.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("money:profile_setup")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile_setup(request):
    profile, _ = FinancialProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = FinancialProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved. Add this month's money snapshot.")
            return redirect("money:budget_create")
    else:
        form = FinancialProfileForm(instance=profile)
    return render(request, "money/profile_setup.html", {"form": form})


@login_required
def budget_create(request):
    profile, _ = FinancialProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = MonthlyBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.profile = profile
            budget.save()
            messages.success(request, "Money snapshot saved.")
            return redirect("money:dashboard")
    else:
        form = MonthlyBudgetForm()
    return render(request, "money/budget_form.html", {"form": form})


@login_required
def dashboard(request):
    profile, _ = FinancialProfile.objects.get_or_create(user=request.user)
    budgets = profile.monthly_budgets.all()
    latest_budget = budgets.first()
    return render(
        request,
        "money/dashboard.html",
        {"profile": profile, "budgets": budgets[:6], "latest_budget": latest_budget},
    )

