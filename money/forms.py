from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import FinancialProfile, MonthlyBudget


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)


class FinancialProfileForm(forms.ModelForm):
    class Meta:
        model = FinancialProfile
        fields = ["emergency_fund_months", "risk_comfort"]


class MonthlyBudgetForm(forms.ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = [
            "month",
            "income",
            "fixed_expenses",
            "flexible_expenses",
            "debt_payments",
        ]
        widgets = {"month": forms.DateInput(attrs={"type": "date"})}

    def clean_month(self):
        month = self.cleaned_data["month"]
        return month.replace(day=1)

