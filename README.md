# Seedcast

Seedcast is an educational Django web application for beginners who have a small amount of money left after monthly expenses. It starts with the user's money picture, calculates a monthly surplus, proposes a simple allocation, and later connects that plan to uncertainty-aware market forecasts, goals, and a grounded copilot.

Seedcast uses paper-money simulations only. It does not provide investment advice.

## First-draft prototype

The current prototype provides a complete database-backed workflow:

1. A user creates an account.
2. The user saves emergency-fund and risk-comfort information.
3. The user submits a monthly income and expense snapshot.
4. Django stores related `FinancialProfile` and `MonthlyBudget` records.
5. The dashboard displays the computed monthly surplus and recent snapshots.

This meets the first-draft foundation requirement with authentication, protected routes, two meaningful related models, forms, validation, views, reusable templates, migrations, and a visible database result.

## Money workflow rules (Parul)

- **Validation:** emergency-fund months must be 0 to 60; snapshot amounts cannot be negative; a snapshot needs at least one non-zero amount; months later than the current month are rejected; a second snapshot for the same month shows a form error instead of a database error.
- **User isolation:** the logged-in user's profile is always taken from the session, never from POST data. Tests in `money/tests.py` (`UserIsolationTests`) prove one user cannot see or write another user's records.
- **Seed Split (initial rules):** `money/allocation.py` splits a positive monthly surplus into an emergency fund (60% under 3 months saved, 30% from 3 to 6 months, 0% at 6+), extra debt payoff (20% when the budget has debt payments), and paper-money practice (the remainder). Buckets always sum exactly to the surplus. The dashboard shows the split with the reason for each bucket.

## Local setup

```powershell
git clone <repository-url>
cd seedcast
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py loaddata demo_assets
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, create an account, and add a monthly snapshot.

Run checks and tests:

```powershell
python manage.py check
python manage.py test
```

## Team ownership

Ownership is divided by complete product slices so every member contributes models, views, URLs, templates, tests, and documentation.

| Owner | Final feature slice | Monday first-draft deliverable | Primary branch |
| --- | --- | --- | --- |
| Parul Mudaliar (`parulm2`) | Money Snapshot, profile, dashboard, health score, Seed Split | Review and extend the `money` models/forms; add profile validation and one allocation rule test | `feature/money-profile` |
| Suriyavardhan Gopal (`gopal8`) | Market data pipeline, Cast Explorer, Stock Detail, Report Card, Copilot integration and evaluation | Add `markets` app with `MarketAsset` and `Forecast` models, sample data, explorer list, and one JSON endpoint | `feature/markets-explorer` |
| Dhruv Thakkar (`dthaker3`) | Forecast ML service, Goal Simulator, Time Machine, shared UI patterns | Add the initial scikit-learn experiment/service contract, `README_AI.md`, and a small feasibility result using frozen sample data | `feature/ai-goals` |

The split reconciles the contribution contract with the later project plan: Suriyavardhan owns market data and AI-agent integration; Dhruv owns the stock-prediction model and financial simulation; Parul owns product scoping and the user money workflow.

## Markets app (Suriyavardhan)

The `markets` app owns curated assets, cached prices and saved forecasts.

| Piece | Where | Notes |
| --- | --- | --- |
| Models | `markets/models.py` | `MarketAsset` 1-to-many `PriceBar` and `Forecast`. `Forecast` follows the TEAM_SETUP.md contract; returns are decimals (0.01 = 1%) and `null` means not computed. |
| Sample data | `markets/fixtures/demo_assets.json` | 10 curated tickers (5 ETFs, 5 stocks). Assets only: no invented prices or forecasts. Load with `python manage.py loaddata demo_assets`. |
| Cached prices | `python manage.py import_prices <file.csv> --source <name>` | CSV header `ticker,date,close[,volume]`. Runs offline, skips unknown tickers and bad rows. |
| Cast Explorer | `/markets/` | Search by ticker/name (`?q=`), filter by type (`?type=etf` or `stock`), empty states. |
| Asset detail | `/markets/<TICKER>/` | Latest forecast with P10 to P90 range and freshness, or a clear "not computed" state; recent prices. |
| JSON API | `/markets/api/assets/` and `/markets/api/forecasts/<TICKER>/` | GET only. Unknown ticker returns 404. A ticker with no forecast returns nulls and `"status": "unavailable"`; forecasts older than 7 days return `"status": "stale"`. |

**Integration with Dhruv's model:** the `intelligence` app writes `Forecast` rows (`asset`, `as_of_date`, `horizon_trading_days`, `expected_return`, `p10_return`, `p90_return`, `probability_positive`, `model_version`, `data_source`). Field names still need final sign-off from Dhruv before merge.

## Git workflow

1. Protect `main`; do not develop directly on it.
2. Each teammate branches from the latest `main` using the branch names above.
3. Keep commits small and descriptive, such as `Add market asset model`.
4. Open a pull request into `main` and request one teammate's review.
5. Before merging, run `python manage.py check` and `python manage.py test`.
6. Pull the latest `main` before starting the next task.

Avoid committing `.env`, API keys, local databases, model weights, or large datasets.

## Monday milestone

- [x] Functional Django project and one app
- [x] Two meaningful related models
- [x] Authentication and protected user data
- [x] Form -> view -> database -> visible result workflow
- [x] Initial tests and reproducible setup
- [x] Market models, sample data, explorer, and JSON endpoint
- [ ] AI technique, inputs/outputs, Django integration path, and feasibility evidence
- [x] One-page updated scope or explicit reference to unchanged P2-A2 scope
- [x] Development status table with owners and dates
- [x] Push public repository and confirm the instructor can access it

See [ROADMAP.md](ROADMAP.md), [README_AI.md](README_AI.md), and the
[assignment compliance matrix](docs/ASSIGNMENT_CHECKLIST.md) for the detailed plan and evidence status.

The current first-draft scope is documented in
[docs/FIRST_DRAFT_SCOPE.md](docs/FIRST_DRAFT_SCOPE.md). Evaluation results must be recorded from actual runs using
[docs/EVALUATION_PLAN.md](docs/EVALUATION_PLAN.md); placeholders must never be presented as completed results.

