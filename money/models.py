from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class FinancialProfile(models.Model):
    class RiskComfort(models.TextChoices):
        CAUTIOUS = "cautious", "Cautious"
        BALANCED = "balanced", "Balanced"
        GROWTH = "growth", "Growth"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="financial_profile",
    )
    emergency_fund_months = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(Decimal("0.0"))],
    )
    risk_comfort = models.CharField(
        max_length=20,
        choices=RiskComfort.choices,
        default=RiskComfort.BALANCED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s financial profile"


class MonthlyBudget(models.Model):
    profile = models.ForeignKey(
        FinancialProfile,
        on_delete=models.CASCADE,
        related_name="monthly_budgets",
    )
    month = models.DateField(help_text="Use the first day of the month.")
    income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    fixed_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    flexible_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    debt_payments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-month", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "month"],
                name="unique_monthly_budget_per_profile",
            )
        ]

    @property
    def surplus(self):
        return self.income - self.fixed_expenses - self.flexible_expenses - self.debt_payments

    def __str__(self):
        return f"{self.profile.user.username}: {self.month:%B %Y}"

