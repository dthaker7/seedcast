from datetime import date
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import FinancialProfile, MonthlyBudget


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)


class FinancialProfileForm(forms.ModelForm):
    class Meta:
        model = FinancialProfile
        fields = ["emergency_fund_months", "risk_comfort"]
        widgets = {
            "emergency_fund_months": forms.NumberInput(attrs={"min": "0", "max": "60", "step": "0.5"}),
        }


class MonthlyBudgetForm(forms.ModelForm):
    """Monthly money snapshot for one user's profile.

    The profile is supplied by the view (never by the POST data), so a user
    can only ever create snapshots for their own profile.
    """

    class Meta:
        model = MonthlyBudget
        fields = [
            "month",
            "income",
            "fixed_expenses",
            "flexible_expenses",
            "debt_payments",
        ]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
            "income": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "fixed_expenses": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "flexible_expenses": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "debt_payments": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def __init__(self, *args, profile=None, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean_month(self):
        month = self.cleaned_data["month"].replace(day=1)
        today = timezone.localdate()
        current_month = date(today.year, today.month, 1)
        if month > current_month:
            raise forms.ValidationError("Snapshots can only be added for this month or earlier.")
        if self.profile is not None:
            existing = MonthlyBudget.objects.filter(profile=self.profile, month=month)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    f"You already have a snapshot for {month:%B %Y}. Pick a different month."
                )
        return month

    def clean(self):
        cleaned = super().clean()
        amounts = [
            cleaned.get(name)
            for name in ("income", "fixed_expenses", "flexible_expenses", "debt_payments")
        ]
        if all(value is not None for value in amounts) and sum(amounts, Decimal("0")) == 0:
            raise forms.ValidationError("Enter at least one non-zero amount for this month.")
        return cleaned

    def save(self, commit=True):
        budget = super().save(commit=False)
        if self.profile is not None:
            budget.profile = self.profile
        if commit:
            budget.save()
        return budget
