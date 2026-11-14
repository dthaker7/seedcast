from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .allocation import build_seed_split
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



class ProfileValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("casey", password="test-password-123")
        self.client.force_login(self.user)

    def test_negative_emergency_fund_is_rejected(self):
        response = self.client.post(
            reverse("money:profile_setup"),
            {"emergency_fund_months": "-1", "risk_comfort": "balanced"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(FinancialProfile.objects.get(user=self.user).emergency_fund_months, Decimal("0.0"))

    def test_unrealistic_emergency_fund_is_rejected(self):
        response = self.client.post(
            reverse("money:profile_setup"),
            {"emergency_fund_months": "61", "risk_comfort": "balanced"},
        )
        self.assertIn("emergency_fund_months", response.context["form"].errors)

    def test_unknown_risk_comfort_is_rejected(self):
        response = self.client.post(
            reverse("money:profile_setup"),
            {"emergency_fund_months": "2", "risk_comfort": "yolo"},
        )
        self.assertIn("risk_comfort", response.context["form"].errors)

    def test_valid_profile_is_saved(self):
        self.client.post(
            reverse("money:profile_setup"),
            {"emergency_fund_months": "4.5", "risk_comfort": "cautious"},
        )
        profile = FinancialProfile.objects.get(user=self.user)
        self.assertEqual(profile.emergency_fund_months, Decimal("4.5"))
        self.assertEqual(profile.risk_comfort, "cautious")


class BudgetValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("drew", password="test-password-123")
        self.profile = FinancialProfile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def post_budget(self, **overrides):
        data = {
            "month": "2026-10-05",
            "income": "1500.00",
            "fixed_expenses": "800.00",
            "flexible_expenses": "300.00",
            "debt_payments": "0.00",
        }
        data.update(overrides)
        return self.client.post(reverse("money:budget_create"), data)

    def test_negative_amount_is_rejected_and_not_saved(self):
        response = self.post_budget(income="-5")
        self.assertIn("income", response.context["form"].errors)
        self.assertFalse(MonthlyBudget.objects.exists())

    def test_missing_required_field_is_rejected(self):
        response = self.post_budget(fixed_expenses="")
        self.assertIn("fixed_expenses", response.context["form"].errors)
        self.assertFalse(MonthlyBudget.objects.exists())

    def test_all_zero_snapshot_is_rejected(self):
        response = self.post_budget(income="0", fixed_expenses="0", flexible_expenses="0", debt_payments="0")
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertFalse(MonthlyBudget.objects.exists())

    def test_future_month_is_rejected(self):
        response = self.post_budget(month="2099-01-01")
        self.assertIn("month", response.context["form"].errors)

    def test_duplicate_month_shows_error_instead_of_crashing(self):
        self.post_budget()
        response = self.post_budget(month="2026-10-20")
        self.assertEqual(response.status_code, 200)
        self.assertIn("month", response.context["form"].errors)
        self.assertEqual(MonthlyBudget.objects.count(), 1)


class UserIsolationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user("owner", password="test-password-123")
        self.other = User.objects.create_user("other", password="test-password-123")
        self.owner_profile = FinancialProfile.objects.create(user=self.owner, emergency_fund_months=Decimal("5"))
        self.other_profile = FinancialProfile.objects.create(user=self.other)
        MonthlyBudget.objects.create(
            profile=self.owner_profile,
            month=date(2026, 9, 1),
            income=Decimal("9999.00"),
            fixed_expenses=Decimal("1.00"),
            flexible_expenses=Decimal("1.00"),
        )

    def test_dashboard_only_shows_own_snapshots(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("money:dashboard"))
        self.assertNotContains(response, "9999")
        self.assertNotContains(response, "September 2026")
        self.assertIsNone(response.context["latest_budget"])

    def test_posted_profile_id_cannot_redirect_budget_to_another_user(self):
        self.client.force_login(self.other)
        self.client.post(
            reverse("money:budget_create"),
            {
                "profile": self.owner_profile.pk,
                "month": "2026-10-01",
                "income": "100.00",
                "fixed_expenses": "10.00",
                "flexible_expenses": "10.00",
                "debt_payments": "0.00",
            },
        )
        self.assertEqual(self.owner_profile.monthly_budgets.count(), 1)
        self.assertEqual(self.other_profile.monthly_budgets.count(), 1)

    def test_profile_update_only_changes_own_profile(self):
        self.client.force_login(self.other)
        self.client.post(
            reverse("money:profile_setup"),
            {"emergency_fund_months": "1", "risk_comfort": "growth"},
        )
        self.owner_profile.refresh_from_db()
        self.assertEqual(self.owner_profile.emergency_fund_months, Decimal("5.0"))
        self.assertEqual(self.owner_profile.risk_comfort, "balanced")

    def test_protected_pages_redirect_anonymous_users(self):
        for name in ("money:dashboard", "money:profile_setup", "money:budget_create"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse("login"), response["Location"])


class SeedSplitRuleTests(TestCase):
    def amounts(self, split):
        return {bucket.key: bucket.amount for bucket in split.buckets}

    def test_no_split_without_positive_surplus(self):
        for surplus in ("0", "-50"):
            split = build_seed_split(Decimal(surplus), Decimal("1"), "balanced", has_debt=True)
            self.assertFalse(split.has_split)
            self.assertIn("no positive surplus", split.message)

    def test_starter_emergency_fund_with_debt(self):
        split = build_seed_split(Decimal("200.00"), Decimal("1"), "balanced", has_debt=True)
        self.assertEqual(
            self.amounts(split),
            {"emergency": Decimal("120.00"), "debt": Decimal("40.00"), "practice": Decimal("40.00")},
        )

    def test_building_emergency_fund_without_debt(self):
        split = build_seed_split(Decimal("200.00"), Decimal("4"), "growth", has_debt=False)
        self.assertEqual(self.amounts(split), {"emergency": Decimal("60.00"), "practice": Decimal("140.00")})

    def test_full_emergency_fund_sends_everything_to_practice(self):
        split = build_seed_split(Decimal("112.00"), Decimal("6"), "cautious", has_debt=False)
        self.assertEqual(self.amounts(split), {"practice": Decimal("112.00")})

    def test_buckets_always_sum_to_surplus_after_rounding(self):
        for surplus in ("0.01", "0.07", "33.33", "101.99", "1234.57"):
            split = build_seed_split(Decimal(surplus), Decimal("2"), "balanced", has_debt=True)
            self.assertEqual(sum(self.amounts(split).values()), Decimal(surplus))

    def test_dashboard_shows_seed_split_for_latest_snapshot(self):
        user = get_user_model().objects.create_user("sam", password="test-password-123")
        profile = FinancialProfile.objects.create(user=user, emergency_fund_months=Decimal("1"))
        MonthlyBudget.objects.create(
            profile=profile,
            month=date(2026, 11, 1),
            income=Decimal("1372.00"),
            fixed_expenses=Decimal("780.00"),
            flexible_expenses=Decimal("420.00"),
            debt_payments=Decimal("60.00"),
        )
        self.client.force_login(user)
        response = self.client.get(reverse("money:dashboard"))
        self.assertContains(response, "Seed Split")
        self.assertContains(response, "$67.20")  # 60% of $112.00
        self.assertContains(response, "$22.40")  # 20% debt and 20% practice
