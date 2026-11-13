from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FinancialProfile, MonthlyBudget


class MonthlyBudgetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("alex", password="test-password-123")
        self.profile = FinancialProfile.objects.create(user=self.user)

    def test_surplus_is_computed_from_budget_fields(self):
        budget = MonthlyBudget.objects.create(
            profile=self.profile,
            month=date(2026, 11, 1),
            income=Decimal("1372.00"),
            fixed_expenses=Decimal("780.00"),
            flexible_expenses=Decimal("420.00"),
            debt_payments=Decimal("60.00"),
        )
        self.assertEqual(budget.surplus, Decimal("112.00"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("money:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_user_can_submit_budget_and_see_result(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("money:budget_create"),
            {
                "month": "2026-11-13",
                "income": "1372.00",
                "fixed_expenses": "780.00",
                "flexible_expenses": "420.00",
                "debt_payments": "60.00",
            },
            follow=True,
        )
        self.assertContains(response, "$112.00")
        self.assertTrue(MonthlyBudget.objects.filter(profile=self.profile).exists())

