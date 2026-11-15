# INFO 490 assignment compliance matrix

This file is the team's source of truth for requirements. A requirement is marked complete only when its evidence exists in the repository or deployed application.

Status values:

- **Complete:** implemented and supported by repository evidence.
- **In progress:** assigned and partially implemented.
- **Planned:** not implemented yet.

## First-draft milestone

| Requirement | Status | Owner | Evidence required |
| --- | --- | --- | --- |
| Updated one-page product scope | Complete | Parul | `docs/FIRST_DRAFT_SCOPE.md` |
| Functional Django project and at least one app | Complete | Shared | `config/`, `money/`, `manage.py` |
| At least two meaningful models | Complete | Parul | `FinancialProfile`, `MonthlyBudget` |
| At least one model relationship | Complete | Parul | User one-to-one profile; profile one-to-many budgets |
| Working views, templates, and URLs | Complete | Parul | Signup, profile, budget, and dashboard routes/templates |
| Functional form and validation | Complete | Parul | Profile and monthly-budget model forms |
| Database-backed visible workflow | Complete | Parul | Budget submission redirects to a dashboard result |
| Initial AI feature and technique identified | Complete | Dhruv | `README_AI.md` |
| AI input, output, and Django interaction documented | Complete | Dhruv | `README_AI.md` workflow section |
| Initial experiment or feasibility evidence | Complete | Dhruv | Frozen dataset, repeatable command, tests, actual metrics, and runtime in `README_AI.md` |
| Development status and roadmap | Complete | Shared | `ROADMAP.md` |
| Reproducible README | Complete | Shared | `README.md`, `.env.example`, `requirements.txt` |
| Instructor-accessible GitHub repository | Complete | Dhruv | Public `dthaker7/seedcast` repository |

## Part 1: Product scope and user experience

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Name, problem, target users, value, features | Complete | Parul | Scope document remains consistent with the product |
| At least three meaningful features | In progress | All | Money, markets, and goals/copilot workflows work end to end |
| Clear navigation and consistent design | In progress | Dhruv | Shared base template; five-item navigation; responsive review |
| Functional forms and user feedback | In progress | Parul | Validation, errors, success messages, empty states. Money forms done and tested (`ProfileValidationTests`, `BudgetValidationTests`); remaining feature forms pending |
| Complete end-to-end workflow | In progress | All | Signup through plan, forecast exploration, and goal/copilot explanation |
| Product differentiation | Complete | Parul | Money-first flow and uncertainty/report-card explanation in scope/README |

## Part 2: Django application development

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Meaningful models, relationships, migrations, CRUD | In progress | All | Each feature app owns models and migrations; create/read/update/delete where relevant |
| Views, templates, inheritance, URLs | In progress | All | Every feature slice includes routes and reusable templates |
| Forms, validation, processing, errors | In progress | All | Profile, budget, allocation, goal, and copilot inputs tested |
| Authentication, protected routes, user isolation | Complete | Parul | `money/tests.py` `UserIsolationTests`: other users' snapshots hidden, posted profile ids ignored, profile edits scoped to the signed-in user, anonymous users redirected to login |
| Meaningful JSON/external API | Planned | Suriyavardhan | Forecast/chart JSON endpoint or cached yfinance integration |
| Data-oriented feature | Planned | Suriyavardhan | Cast Explorer search/filtering and visualizations |

## Part 3: AI integration

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Meaningful AI feature inside Django | Planned | Dhruv | Saved forecast consumed by Cast Explorer/Stock Detail |
| Model-selection rationale | In progress | Dhruv | Compare selected approach with at least one feasible alternative |
| Full input-to-output workflow | In progress | Dhruv | Code and documentation trace preprocessing through database/UI |
| Integration depth | Planned | Dhruv and Suriyavardhan | AI uses cached market/application data, not a disconnected demo |
| Reliability and graceful failure | Planned | Dhruv | Tests for missing/stale data, model errors, and unavailable output |
| Grounded LLM behavior | Planned | Suriyavardhan | Structured computed context; refusal for unavailable data/stock picks |

## Part 4: evaluation, testing, and improvement

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Relevant evaluation metrics | Planned | Suriyavardhan | Forecast calibration/error, baseline comparison, latency, workflow completion |
| Five realistic tests | Planned | Suriyavardhan | Complete every field in `docs/EVALUATION_PLAN.md` using actual runs |
| Two genuine failure cases | Planned | All | Document cause, impact, and improvement for observed failures |
| One measured improvement | Planned | All | Before -> modification -> after evidence without fabricated results |
| Automated application tests | In progress | All | CI passes; each pull request adds relevant tests |

## Part 5: deployment and production readiness

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Working deployment | Planned | Dhruv | Primary workflow runs on the selected host |
| Infrastructure requirements | Planned | Dhruv | CPU, RAM, storage, database, scheduled jobs, inference needs |
| Two-option cost comparison | Planned | Dhruv | Realistic assumptions and monthly estimates |
| 10,000-DAU scalability analysis | Planned | Dhruv | Bottlenecks, caching, jobs, database, and AI cost assumptions |
| Security and reliability | In progress | All | Environment variables, permissions, validation, logging, rate limits, privacy |

## Part 6: documentation and reproducibility

| Requirement | Status | Owner | Definition of done |
| --- | --- | --- | --- |
| Code, migrations, AI code, requirements, gitignore, README | In progress | All | Update dependencies when AI/data code lands |
| Complete README setup instructions | Complete for prototype | Shared | A clean clone can install, migrate, test, and run |
| AI documentation | In progress | Dhruv | Update `README_AI.md` with actual model, results, limitations, safety |
| Readable, separated, non-duplicated code | In progress | All | Pull-request review and CI required before merge |
| No exposed credentials or model weights | Complete for current repository | All | `.gitignore`; secret review before every merge |

## Evidence rules

- Never mark a feature complete because a document says it is planned.
- Do not enter invented evaluation scores, model accuracy, latency, costs, or user-test results.
- Each completed functional requirement needs code plus a test, screenshot, command output, or deployed demonstration.
- Each teammate must contribute technical commits across Django models, views/services, tests, or AI/data integration.
- Keep `.env`, API keys, `db.sqlite3`, private user data, large datasets, and model weights out of Git.

