# Seedcast poster content

## Header

**Seedcast**  
Money-first planning with transparent market forecasts

Dhruv Thakkar - dthaker3@illinois.edu  
Parul Mudaliar - parulm2@illinois.edu  
Suriyavardhan Gopal - gopal8@illinois.edu

## Problem and motivation

- Beginning investors may have a small monthly surplus but no clear next step.
- Budgeting tools and market screeners separate personal readiness from market information.
- Seedcast calculates a surplus, explains an initial allocation, and shows saved forecasts with uncertainty and freshness.
- Educational paper-money simulation only. No personalized investment advice.

## System architecture

Money path: user input -> Django forms and validation -> FinancialProfile and MonthlyBudget -> Seed Split dashboard.

AI path: frozen OHLCV data -> pandas feature pipeline -> scikit-learn gradient boosting -> validation and saved Forecast -> Cast Explorer, asset detail, and JSON API.

Normal web requests read saved predictions. Model training runs offline through `python manage.py load_demo_market_data`.

## Evaluation and analytics

- Frozen Apple sample: 506 daily rows from February 2015 to February 2017.
- 436 usable feature rows after warm-up and target construction.
- Chronological holdout: 327 training rows and 88 test rows.
- 21 overlapping training labels purged before evaluation.
- Baseline: constant training-set mean 21-day return.

| Metric | Baseline | Gradient boosting |
| --- | ---: | ---: |
| MAE | 0.054991 | 0.056230 |
| RMSE | 0.065537 | 0.069410 |
| Directional accuracy | 27.27% | 40.91% |
| R-squared | n/a | -0.662852 |

## Key results

- The integrated command stores 506 real cached AAPL prices and one model-generated Django forecast.
- Directional accuracy increased by 13.64 percentage points over the baseline.
- Error increased: model MAE was 2.25% worse and RMSE was 5.91% worse than the baseline.
- The combined Django, markets, money, and AI suite passes 53 automated tests.

## Limitations and future work

- One old ticker cannot represent current market regimes.
- The probability-positive value uses empirical training residuals and is not calibrated.
- A single holdout is weaker than walk-forward evaluation.
- Next: licensed current data, more assets, walk-forward validation, calibrated intervals, and production monitoring.

## Footer

GitHub: https://github.com/dthaker7/seedcast

Dataset attribution: Plotly datasets, MIT License. The upstream market-data vendor is not identified, so the sample is limited to educational feasibility work.

