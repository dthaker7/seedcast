"""Seed Split: rule-based allocation of a monthly surplus.

These are transparent, educational rules (not investment advice). They take
only values the user has saved in the money app and return a split of the
monthly surplus into three buckets. Every rule is deterministic so it can be
unit-tested and explained back to the user.

Rules
-----
1. No positive surplus -> no split. The user is told to close the gap first.
2. Emergency fund share depends on months of expenses already saved:
   - below 3 months  -> 60% of surplus
   - 3 to <6 months  -> 30% of surplus
   - 6 months or more -> 0%
3. Extra debt payoff gets 20% when the budget includes debt payments.
4. Whatever remains goes to the paper-money practice bucket, which later
   connects to Cast Explorer simulations. Risk comfort only changes the
   label/explanation of that bucket, never the arithmetic.
5. Amounts are rounded to cents; the practice bucket absorbs rounding so the
   buckets always add up exactly to the surplus.
"""

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")

EMERGENCY_STARTER_MONTHS = Decimal("3")
EMERGENCY_FULL_MONTHS = Decimal("6")
EMERGENCY_SHARE_STARTER = Decimal("0.60")
EMERGENCY_SHARE_BUILDING = Decimal("0.30")
DEBT_SHARE = Decimal("0.20")

PRACTICE_NOTES = {
    "cautious": "Practice with broad, lower-volatility funds in the simulator.",
    "balanced": "Practice with a mix of broad funds and a few individual assets.",
    "growth": "Practice exploring higher-volatility assets, with paper money only.",
}


@dataclass
class Bucket:
    key: str
    label: str
    amount: Decimal
    share: Decimal
    reason: str


@dataclass
class SeedSplit:
    surplus: Decimal
    buckets: list = field(default_factory=list)
    message: str = ""

    @property
    def has_split(self):
        return bool(self.buckets)


def _cents(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def emergency_share(emergency_fund_months):
    months = Decimal(emergency_fund_months)
    if months < EMERGENCY_STARTER_MONTHS:
        return EMERGENCY_SHARE_STARTER
    if months < EMERGENCY_FULL_MONTHS:
        return EMERGENCY_SHARE_BUILDING
    return Decimal("0")


def build_seed_split(surplus, emergency_fund_months, risk_comfort, has_debt):
    """Return a SeedSplit for the given saved values."""
    surplus = _cents(Decimal(surplus))
    if surplus <= 0:
        return SeedSplit(
            surplus=surplus,
            message=(
                "There is no positive surplus this month, so Seed Split does not "
                "allocate anything. Review flexible expenses first."
            ),
        )

    e_share = emergency_share(emergency_fund_months)
    d_share = DEBT_SHARE if has_debt else Decimal("0")

    emergency_amount = _cents(surplus * e_share)
    debt_amount = _cents(surplus * d_share)
    practice_amount = surplus - emergency_amount - debt_amount
    practice_share = Decimal("1") - e_share - d_share

    buckets = []
    if emergency_amount > 0:
        buckets.append(
            Bucket(
                "emergency",
                "Emergency fund",
                emergency_amount,
                e_share,
                f"You have {emergency_fund_months} months saved; the goal is "
                f"{EMERGENCY_FULL_MONTHS} months.",
            )
        )
    if debt_amount > 0:
        buckets.append(
            Bucket(
                "debt",
                "Extra debt payoff",
                debt_amount,
                d_share,
                "Your budget includes debt payments, so part of the surplus speeds up payoff.",
            )
        )
    if practice_amount > 0:
        buckets.append(
            Bucket(
                "practice",
                "Paper-money practice",
                practice_amount,
                practice_share,
                PRACTICE_NOTES.get(risk_comfort, PRACTICE_NOTES["balanced"]),
            )
        )

    return SeedSplit(
        surplus=surplus,
        buckets=buckets,
        message="Educational split of this month's surplus. Not investment advice.",
    )


def seed_split_for_budget(profile, budget):
    """Convenience wrapper used by views: build a split from saved records."""
    return build_seed_split(
        surplus=budget.surplus,
        emergency_fund_months=profile.emergency_fund_months,
        risk_comfort=profile.risk_comfort,
        has_debt=budget.debt_payments > 0,
    )
