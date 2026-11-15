# Seedcast AI plan

## Meaningful AI feature

The first AI feature is an uncertainty-aware 21-trading-day market forecast for a small, curated set of liquid stocks and ETFs. The application will show an expected return, P10-P90 interval, probability of a positive month, confidence, and the most important input indicators. It will not produce buy or sell labels.

## First-draft feasibility experiment

The first-draft experiment intentionally tests the smallest technically relevant question: can a repeatable scikit-learn pipeline transform frozen historical market data into a time-ordered 21-trading-day forecast and compare it with a simple baseline?

- Frozen input: Plotly's historical Apple daily dataset, stored at `data/aapl_daily_2015_2017.csv` so execution does not call a live API.
- Price used: adjusted close, with volume as the other raw input.
- Features: one-day return, 5-day and 21-day momentum, 21-day volatility, 10/50-day moving-average gap, and 5/21-day volume ratio.
- Target: adjusted-close return over the next 21 trading days.
- Split: final 20% of usable rows for testing. Candidate training rows come from the first 80%, but any row whose 21-day target reaches the test feature period is purged. Rows are never shuffled.
- Baseline: one constant prediction equal to the mean 21-day return in the training set.
- Model: scikit-learn `GradientBoostingRegressor` with fixed hyperparameters and `random_state=42`.
- Metrics: mean absolute error (MAE), root mean squared error (RMSE), directional accuracy, and model R-squared.

Run from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m ai_feasibility --output artifacts/ai_feasibility_results.json
```

The JSON output records the frozen file's SHA-256 hash, row counts, split dates, metrics, and measured runtime. The recorded results section below must be updated only from actual command output.

## Recorded results

Executed on November 15, 2026 with:

```powershell
python -m ai_feasibility --output artifacts/ai_feasibility_results.json
```

The frozen dataset's canonical SHA-256 was `04053fd4ab339dd81a2bd14153e4be4fd88ae209fbc7aca29bc1096a3cbe7f27`. The fingerprint normalizes text line endings to LF so it remains stable on Windows and Linux. Feature warm-up and the 21-day target reduced 506 raw rows to 436 usable observations. The chronological boundary produced 348 candidate training rows and 88 test rows. To prevent label overlap, 21 candidate rows whose forward target used prices from the test feature period were purged. The final training set therefore contains 327 rows; its last target date is September 12, 2016, before the first test feature date of September 13, 2016.

| Metric | Mean-return baseline | Gradient boosting model |
| --- | ---: | ---: |
| MAE | 0.054991 | 0.056230 |
| RMSE | 0.065537 | 0.069410 |
| Directional accuracy | 27.27% | 40.91% |
| R-squared | Not applicable | -0.662852 |

Measured pipeline runtime was **0.0527 seconds** on the development machine. The model's MAE was 2.25% worse and its RMSE was 5.91% worse than the fixed training-mean baseline on this holdout. Directional accuracy was higher, but the negative R-squared, worse error metrics, and small, old, single-ticker sample show that this configuration is not a reliable forecasting model. The experiment still establishes technical feasibility: the frozen data, feature pipeline, chronological purge, model training, evaluation, and result recording are repeatable. It does not justify investment decisions. The raw execution record is stored in `artifacts/ai_feasibility_results.json`.

## Django workflow

`Cached market data -> feature service -> offline training command -> forecast validation -> Forecast database record -> Cast Explorer / Stock Detail / Report Card`

The online request path reads saved forecasts. It does not retrain the model while a user waits.

## Copilot plan

The later copilot will receive only structured values that Seedcast already computed, such as surplus, risk comfort, allocation amounts, goal probability, and forecast ranges. It will explain those values and refuse requests that require unavailable data or personalized stock-picking advice.

## Reliability and safety

- Validate missing, stale, or insufficient price history before inference.
- Keep a frozen sample dataset so the demo does not depend on a live API.
- Catch pipeline and model failures without replacing missing forecasts with zero.
- Display data freshness, uncertainty, track record, and an educational-use notice.
- Store API keys only in environment variables.
- Do not claim accuracy until tests produce measured results.

## Limitations

- This is one ticker over roughly two years, so it is feasibility evidence rather than a production-quality market model.
- A single chronological holdout is weaker than the planned walk-forward evaluation.
- The experiment predicts a point return only; P10-P90 quantile models and probability calibration remain future work.
- Market regimes after February 2017 are not represented.
- Feature engineering is deliberately small and does not yet include RSI or MACD.
- The experiment treats the supplied adjusted-close series as point-in-time input. A production pipeline must verify point-in-time corporate-action handling rather than recomputing historical adjustments with future information.
- Model performance may be worse than the baseline. The purpose is to measure feasibility honestly, not to claim predictability.
- The dataset is a frozen educational sample from Plotly's MIT-licensed datasets repository. The repository does not identify this file's upstream market-data vendor, so the team must select and license an appropriate production source before deployment. Attribution and the license notice are stored under `data/`.

