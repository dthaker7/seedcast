# Seedcast AI status

This file is the shared handoff for AI-related work. Update it in the same pull request as any change to the dataset, features, model, evaluation, saved forecast interface, or copilot grounding.

## Current verified experiment

- Branch: `feature/ai-goals`
- Command: `python -m ai_feasibility --output artifacts/ai_feasibility_results.json`
- Dataset: `data/aapl_daily_2015_2017.csv`
- Forecast target: adjusted-close return over the next 21 trading days
- Evaluation: fixed chronological 80/20 train/test split
- Baseline: training-set mean target return
- Model: scikit-learn `GradientBoostingRegressor`
- Frozen dataset canonical SHA-256 (LF-normalized): `04053fd4ab339dd81a2bd14153e4be4fd88ae209fbc7aca29bc1096a3cbe7f27`
- Split: 348 candidate training rows and 88 test rows; 21 overlapping labels purged, leaving 327 training rows whose targets end on 2016-09-12 before the 2016-09-13 test period
- Baseline: MAE 0.054991; RMSE 0.065537; directional accuracy 27.27%
- Gradient boosting: MAE 0.056230; RMSE 0.069410; directional accuracy 40.91%; R-squared -0.662852
- Recorded runtime: 0.0527 seconds
- Raw result: `artifacts/ai_feasibility_results.json`

## Interface contract for teammates

The experiment remains offline training, but `python manage.py load_demo_market_data` now writes its real AAPL result through the Django `Forecast` model. Web requests read the saved result and never retrain the model:

`frozen/cached prices -> feature builder -> trained model -> validated forecast record -> markets UI/API`

Suriyavardhan's market app should consume saved forecast records rather than train a model during a web request. Parul's money app should not import experiment code directly.

## How to update this file

1. Run the experiment and tests from a clean branch.
2. Record the exact dataset hash, command, split dates, metrics, and runtime from output.
3. State any failure or regression, even if the model performs worse than the baseline.
4. Update `README_AI.md` when methodology or limitations change.
5. Add a dated changelog entry below with the commit or pull request.

## Changelog

- 2026-11-15: Purged 21 training rows whose forward labels overlapped the test feature period and reran the experiment. The leakage-free model was worse than the baseline on MAE/RMSE; the limitation is recorded without hiding the result.
- 2026-11-13: Added the frozen-data experiment and recorded the initial run. Those metrics were superseded after the label-overlap audit.
