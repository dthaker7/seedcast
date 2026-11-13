# Seedcast AI plan

## Meaningful AI feature

The first AI feature is an uncertainty-aware 21-trading-day market forecast for a small, curated set of liquid stocks and ETFs. The application will show an expected return, P10-P90 interval, probability of a positive month, confidence, and the most important input indicators. It will not produce buy or sell labels.

## Proposed technique

- Input: cached daily OHLCV data for a ticker, transformed into momentum, RSI, MACD, rolling volatility, and volume-trend features.
- Model: scikit-learn gradient boosting, including quantile-loss models for lower and upper bounds.
- Validation: time-ordered walk-forward evaluation to avoid look-ahead leakage.
- Output: forecast values and evaluation metadata saved in Django models for the UI and JSON endpoints.
- Baseline: a simple historical-return or buy-and-hold baseline evaluated on the same dates.

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

## First-draft evidence still required

Dhruv will add a reproducible experiment or management command that trains on frozen sample data and records at least one real metric and runtime. The team should report actual results only; placeholder metrics must not be presented as evidence.

