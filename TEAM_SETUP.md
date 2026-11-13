# Seedcast — Team Setup and Collaboration Guide

**Course:** INFO 490 · Team 8  
**Repository:** https://github.com/dthaker7/seedcast  
**Working deadline for first draft:** Monday, November 16, 2026 (confirm in Canvas)  
**Project:** Educational finance planning and uncertainty-aware stock forecasting. No live trading or investment advice.

## 1. Before you begin

1. Sign in to GitHub and **accept the collaborator invitation** for `dthaker7/seedcast`. The repository is public, so anyone can view or clone it, but pushing requires write permission.
2. Install **Git**, **Python 3.14** (the version used in repository CI), and **VS Code** or another editor. Ensure `git --version` and `python --version` work in PowerShell. If Windows uses `py`, substitute `py -3.14` for `python` below.
3. Read `README.md`, `ROADMAP.md`, and `docs/ASSIGNMENT_CHECKLIST.md`. Review the project wireframes before building UI.
4. **Don't edit or push `main` directly.** Use your assigned feature branch and open a pull request for review.

## 2. Who works on what?

| Teammate | GitHub account invited | Branch | First tasks |
| --- | --- | --- | --- |
| **Parul Mudaliar** | `ParulMudaliar` | `feature/money-profile` | Review existing `money` models, forms, views and dashboard; add validation, user-isolation tests, and initial Seed Split rules. Extend existing functionality rather than recreating it. |
| **Suriyavardhan Gopal** | `suriya-gopal` | `feature/markets-explorer` | Add a market-data Django app with asset and price/forecast storage, curated sample records, Cast Explorer listing, and a JSON endpoint. Coordinate forecast schema with Dhruv before integration. |
| **Dhruv Thakkar** | `dthaker7` | `feature/ai-goals` | Complete the reproducible ML feasibility experiment, forecasting contract, Goal Simulator and Time Machine. Coordinate stored forecast fields with Suriyavardhan. |

These GitHub account names reflect the invitations reported for this repository. If you use a different GitHub account, tell the repository owner.

**Current baseline:** `main` contains authentication and a database-backed financial profile / monthly budget workflow. The full market and AI features are **not** on `main` yet. Dhruv also has local, uncommitted AI experiment changes: other teammates should not assume those changes are available on GitHub.

## 3. Clone the repository (first time only)

Open **PowerShell** or the VS Code terminal in the folder where you want the project, then run:

```powershell
git clone https://github.com/dthaker7/seedcast.git
cd seedcast
```

Select **only your assigned branch**:

**Parul:**

```powershell
git switch feature/money-profile
```

**Suriyavardhan:**

```powershell
git switch feature/markets-explorer
```

**Dhruv:** If the project is already on your laptop and your experiment contains uncommitted work, **do not clone over the folder or switch branches**. Continue working in the existing checkout and verify `git branch --show-current` returns `feature/ai-goals`.

Confirm your branch:

```powershell
git branch --show-current
git status
```

## 4. Install and run Django (Windows PowerShell)

From the `seedcast` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in a browser. Create a test account, complete your financial profile, enter a monthly budget, and verify the dashboard updates.

**If the virtual environment won't activate:** use `cmd.exe` and `.venv\Scripts\activate.bat`, or run `.\.venv\Scripts\python.exe` directly instead of `python` for the Django commands. Avoid changing your system-wide execution policy.

**If port 8000 is busy:** `python manage.py runserver 8001`, then use http://127.0.0.1:8001/.

**Environment variables:** `.env.example` documents optional settings, but the current Django settings read operating-system environment variables directly; simply copying `.env.example` to `.env` does **not** automatically load it. Local development works with the existing development defaults. Never commit `.env` or an API key. Ask Dhruv before adding any external API credential.

**Python compatibility:** CI uses Python 3.14 with Django 6.1.1. Other Python versions have not been verified by the team's CI; if dependency installation fails, align with CI.

## 5. Run checks before every push

Stop the development server with `Ctrl+C`, then run:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

If you add or change database models, first create and review migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Then run the three checks again. The GitHub Actions **Django checks** workflow runs on pushes to `main` and `feature/**`, and on pull requests targeting `main`.

## 6. Daily Git workflow

Start each session on your assigned branch:

```powershell
git status
git branch --show-current
git pull --ff-only origin feature/money-profile
```

Replace `feature/money-profile` with **your own branch**. `git pull --ff-only` may stop if you have conflicting/uncommitted local work; don't force it or discard changes. Ask in the team chat if unsure.

After writing and testing your feature:

```powershell
git status
git add <specific-files-you-changed>
git commit -m "feat(money): improve profile validation"
git push origin feature/money-profile
```

Again, replace the branch, file paths, and commit message to match your work. Prefer staging specific files over `git add .` so you do not accidentally include local databases, credentials, datasets, or unrelated edits.

**Pull request workflow:** On GitHub, open **Pull requests → New pull request**. Set **base** to `main` and **compare** to your feature branch. Explain what changed, how to test, screenshots (for UI), and any known limitations. Request review from at least one other teammate; merge only after review and green CI. Never use a force push or reset on a shared branch without coordinating.

## 7. Integration agreements

The Django app boundaries documented in `ROADMAP.md` are:

- **Money / Parul:** `FinancialProfile`, monthly budget/surplus, risk comfort, saved allocation. Use existing `money` app.
- **Markets / Suriyavardhan:** assets, historical prices, saved forecasts, market browsing and chart/API endpoints. The Copilot receives *computed* data rather than inventing figures.
- **Intelligence / Dhruv:** offline training, forecasting, model evaluation, simulations. Training does not run inside a normal web request.

**Proposed forecast interface — agree on exact field names before coding:**

```json
{
  "ticker": "AAPL",
  "as_of_date": "YYYY-MM-DD",
  "horizon_trading_days": 21,
  "expected_return": null,
  "p10_return": null,
  "p90_return": null,
  "probability_positive": null,
  "model_version": null,
  "data_source": null
}
```

`null` means not yet computed; **never replace missing predictions with invented values**. Return units should be documented consistently (e.g., decimal `0.01` means 1%). Suriyavardhan and Dhruv must agree how to persist forecast timestamps, uncertainty, validation results and freshness. This JSON is a **planning contract**, not a claim that the endpoint exists.

**Code ownership rules:** Keep your code inside your own Django app where practical. Don't modify teammates' models or shared files without coordinating. Do not import views/forms across apps; use services/models and agreed data interfaces. Resolve conflicting migrations together.

## 8. Monday first-draft checklist

- [ ] All teammates have accepted invitations and confirmed write access.
- [ ] Each teammate can clone their branch and run the Django app.
- [ ] Each teammate can run the checks and tests successfully.
- [ ] Parul: strengthen profile validation and cross-user isolation tests.
- [ ] Suriyavardhan: implement and verify market models, demo data, explorer list and first JSON endpoint.
- [ ] Dhruv: keep recorded feasibility experiment reproducible; publish it to **`feature/ai-goals` only** when ready for review.
- [ ] Update `docs/ASSIGNMENT_CHECKLIST.md` only for requirements with actual evidence.
- [ ] Confirm the exact submission instructions and date in Canvas.

The final project has additional requirements; see `ROADMAP.md` and `docs/EVALUATION_PLAN.md`. No one should claim unbuilt features or invented results are complete.

## 9. Troubleshooting

| Issue | What to try |
| --- | --- |
| `Permission denied` when pushing | Accept the GitHub collaborator invitation and ensure Git authenticates as the invited account. |
| `fatal: not a git repository` | Run `cd seedcast` and check that the folder has the repo's `.git` metadata. |
| `python` not found | Install Python 3.14, open a new terminal, or use the Windows `py -3.14` launcher. |
| `No module named django` | Activate `.venv` and reinstall `requirements.txt`. |
| `no such table` / migration error | Run `python manage.py migrate` in the active virtual environment. |
| `port is already in use` | Stop the other server or start with `python manage.py runserver 8001`. |
| Conflicts after pulling | **Do not delete or overwrite your work.** Tell the group which files conflict and coordinate a merge. |
| CI fails | Open the failed GitHub Actions job, read the first relevant error, reproduce it locally and push a fix to your branch. |

## 10. References

- [Repository and README](https://github.com/dthaker7/seedcast)
- [Roadmap](https://github.com/dthaker7/seedcast/blob/main/ROADMAP.md)
- [Assignment compliance matrix](https://github.com/dthaker7/seedcast/blob/main/docs/ASSIGNMENT_CHECKLIST.md)
- [AI design plan](https://github.com/dthaker7/seedcast/blob/main/README_AI.md)
- [GitHub Actions](https://github.com/dthaker7/seedcast/actions)

**Team rule:** Work on your own branch, test before pushing, review pull requests, and keep private financial information and credentials out of Git.
