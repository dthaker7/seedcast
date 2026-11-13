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

## Local setup

```powershell
git clone <repository-url>
cd seedcast
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
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
- [ ] Market models, sample data, explorer, and JSON endpoint
- [ ] AI technique, inputs/outputs, Django integration path, and feasibility evidence
- [ ] One-page updated scope or explicit reference to unchanged P2-A2 scope
- [ ] Development status table with owners and dates
- [ ] Push repository and confirm the instructor can access it

See [ROADMAP.md](ROADMAP.md) and [README_AI.md](README_AI.md) for the detailed plan.

