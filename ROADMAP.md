# Seedcast roadmap

## Monday, November 16, 2026 milestone

The first-draft milestone was completed for the team's confirmed Monday, November 16, 2026 deadline.

| Task | Current status | Responsible member | Expected completion |
| --- | --- | --- | --- |
| Django core features | Money workflow merged with validation, user-isolation tests, and initial Seed Split rules | Parul, with shared setup by Dhruv | Complete Nov. 14 |
| Database and APIs | Market models, demo assets, Cast Explorer, and forecast/asset JSON endpoints merged and tested | Suriyavardhan | Complete Nov. 15 |
| AI integration | Architecture documented; frozen-data feasibility experiment records actual baseline/model metrics and runtime | Dhruv | Complete Nov. 15 |
| Evaluation and testing | Money, markets, and AI automated tests pass; five final-product evaluation cases remain for the final submission | Suriyavardhan | First-draft evidence complete Nov. 15 |
| Deployment | Local run path documented; hosting not required for first draft | Dhruv | Nov. 16 |
| Documentation | README, scope update, AI plan, compliance matrix, and four money-workflow screenshots added | Parul | Complete Nov. 16 |

## Final ownership through December 8

### Parul: money and allocation

- Five-step financial profile and validation
- Monthly Money Snapshot and health score
- Dashboard and Seed Split allocation rules
- User research notes and usability-test coordination
- Unit and form tests for money and allocation workflows

### Suriyavardhan: markets and grounded explanations

- Market data ingestion and cached/frozen dataset
- Cast Explorer, search/filtering, Stock Detail, and forecast JSON API
- Report Card metrics and automated evaluation support
- Copilot integration using computed values supplied by the other apps
- Integration tests for market data, API failures, and copilot grounding

### Dhruv: predictive modeling and simulation

- Feature engineering and walk-forward model training
- Quantile forecasts, baselines, and saved inference interface
- Goal Simulator and Time Machine calculations
- Shared visual system based on the wireframes
- Model documentation, limitations, and deployment-cost analysis

## Integration contracts

- `money` owns the user's surplus, risk comfort, and saved allocation.
- `markets` owns assets, price history, stored forecasts, and market-facing APIs.
- `intelligence` will own training/inference services and simulations, but writes forecast results through the `markets` model interface.
- The copilot receives a small structured context object assembled from saved records; it never calculates financial values itself.
- No app imports another app's view or form. Cross-app behavior goes through models or service functions.

## Definition of done for every pull request

- Relevant migration included
- New behavior covered by at least one test
- `python manage.py check` passes
- `python manage.py test` passes
- No secrets, local database, large data, or model weights committed
- README or AI documentation updated when setup or behavior changes
- One teammate reviews before merge

