from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


FEATURE_COLUMNS = (
    "daily_return",
    "momentum_5",
    "momentum_21",
    "volatility_21",
    "ma_gap_10_50",
    "volume_ratio_5_21",
)
FORECAST_HORIZON_DAYS = 21
TRAIN_FRACTION = 0.80
RANDOM_STATE = 42


@dataclass(frozen=True)
class ExperimentResult:
    dataset_path: str
    dataset_sha256: str
    raw_rows: int
    usable_rows: int
    candidate_train_rows: int
    purged_train_rows: int
    train_rows: int
    test_rows: int
    train_start: str
    train_end: str
    train_target_end: str
    test_start: str
    test_end: str
    forecast_horizon_trading_days: int
    baseline_description: str
    baseline_mae: float
    baseline_rmse: float
    baseline_directional_accuracy: float
    model_description: str
    model_mae: float
    model_rmse: float
    model_r2: float
    model_directional_accuracy: float
    runtime_seconds: float
    executed_at_utc: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ForecastPrediction:
    as_of_date: str
    horizon_trading_days: int
    expected_return: float
    p10_return: float
    p90_return: float
    probability_positive: float
    model_version: str


def file_sha256(path: Path) -> str:
    """Hash text content with canonical LF endings for cross-platform stability."""
    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def load_frozen_market_data(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "AAPL.Adjusted", "AAPL.Volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    frame = frame.loc[:, ["Date", "AAPL.Adjusted", "AAPL.Volume"]].rename(
        columns={"AAPL.Adjusted": "adjusted_close", "AAPL.Volume": "volume"}
    )
    frame = frame.sort_values("Date").reset_index(drop=True)

    if frame.empty:
        raise ValueError("Dataset contains no rows.")
    if frame["Date"].duplicated().any():
        raise ValueError("Dataset contains duplicate dates.")
    if frame[["adjusted_close", "volume"]].isna().any().any():
        raise ValueError("Dataset contains missing price or volume values.")
    if (frame[["adjusted_close", "volume"]] <= 0).any().any():
        raise ValueError("Price and volume values must be positive.")

    return frame


def build_supervised_dataset(market_data: pd.DataFrame) -> pd.DataFrame:
    frame = market_data.copy()
    close = frame["adjusted_close"]
    volume = frame["volume"]
    daily_return = close.pct_change()

    frame["daily_return"] = daily_return
    frame["momentum_5"] = close.pct_change(5)
    frame["momentum_21"] = close.pct_change(FORECAST_HORIZON_DAYS)
    frame["volatility_21"] = daily_return.rolling(FORECAST_HORIZON_DAYS).std()
    frame["ma_gap_10_50"] = close.rolling(10).mean() / close.rolling(50).mean() - 1
    frame["volume_ratio_5_21"] = (
        volume.rolling(5).mean() / volume.rolling(FORECAST_HORIZON_DAYS).mean() - 1
    )
    frame["target_return_21d"] = (
        close.shift(-FORECAST_HORIZON_DAYS) / close - 1
    )
    frame["target_date"] = frame["Date"].shift(-FORECAST_HORIZON_DAYS)

    supervised = frame.dropna(
        subset=[*FEATURE_COLUMNS, "target_return_21d", "target_date"]
    ).reset_index(drop=True)
    if len(supervised) < 100:
        raise ValueError("At least 100 usable rows are required for the experiment.")
    return supervised


def latest_feature_row(market_data: pd.DataFrame) -> pd.DataFrame:
    """Build one inference row using only information available on its date."""
    frame = market_data.copy()
    close = frame["adjusted_close"]
    volume = frame["volume"]
    daily_return = close.pct_change()
    frame["daily_return"] = daily_return
    frame["momentum_5"] = close.pct_change(5)
    frame["momentum_21"] = close.pct_change(FORECAST_HORIZON_DAYS)
    frame["volatility_21"] = daily_return.rolling(FORECAST_HORIZON_DAYS).std()
    frame["ma_gap_10_50"] = close.rolling(10).mean() / close.rolling(50).mean() - 1
    frame["volume_ratio_5_21"] = (
        volume.rolling(5).mean() / volume.rolling(FORECAST_HORIZON_DAYS).mean() - 1
    )
    latest = frame.dropna(subset=list(FEATURE_COLUMNS)).tail(1)
    if latest.empty:
        raise ValueError("Dataset does not contain enough history for inference.")
    return latest


def _gradient_boosting_model(*, loss="squared_error", alpha=0.9):
    return GradientBoostingRegressor(
        loss=loss,
        alpha=alpha,
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        min_samples_leaf=8,
        random_state=RANDOM_STATE,
    )


def predict_latest_return(dataset_path: Path) -> ForecastPrediction:
    """Train on all labeled rows and forecast the latest frozen observation.

    Quantile models provide the displayed P10/P90 range. The probability of a
    positive return is an empirical residual estimate, not a calibrated
    probability; this limitation is surfaced in the documentation and UI.
    """
    market_data = load_frozen_market_data(dataset_path)
    supervised = build_supervised_dataset(market_data)
    inference = latest_feature_row(market_data)
    x_train = supervised.loc[:, FEATURE_COLUMNS]
    y_train = supervised["target_return_21d"]
    x_latest = inference.loc[:, FEATURE_COLUMNS]

    point_model = _gradient_boosting_model()
    lower_model = _gradient_boosting_model(loss="quantile", alpha=0.10)
    upper_model = _gradient_boosting_model(loss="quantile", alpha=0.90)
    point_model.fit(x_train, y_train)
    lower_model.fit(x_train, y_train)
    upper_model.fit(x_train, y_train)

    expected = float(point_model.predict(x_latest)[0])
    lower = float(lower_model.predict(x_latest)[0])
    upper = float(upper_model.predict(x_latest)[0])
    lower, upper = sorted((lower, upper))
    residuals = y_train.to_numpy() - point_model.predict(x_train)
    probability_positive = float(np.mean(expected + residuals > 0))

    return ForecastPrediction(
        as_of_date=inference.iloc[0]["Date"].date().isoformat(),
        horizon_trading_days=FORECAST_HORIZON_DAYS,
        expected_return=expected,
        p10_return=lower,
        p90_return=upper,
        probability_positive=probability_positive,
        model_version="gbr-v1-frozen-aapl",
    )


def time_ordered_split(
    supervised: pd.DataFrame,
    train_fraction: float = TRAIN_FRACTION,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not 0.5 <= train_fraction < 1.0:
        raise ValueError("train_fraction must be at least 0.5 and less than 1.0.")
    split_index = int(len(supervised) * train_fraction)
    candidate_train = supervised.iloc[:split_index].copy()
    test = supervised.iloc[split_index:].copy()
    if candidate_train.empty or test.empty:
        raise ValueError("Time split produced an empty train or test set.")
    test_start = test["Date"].min()
    train = candidate_train.loc[candidate_train["target_date"] < test_start].copy()
    if train.empty:
        raise ValueError("Purging overlapping labels produced an empty training set.")
    if train["Date"].max() >= test["Date"].min():
        raise ValueError("Time split is not strictly chronological.")
    if train["target_date"].max() >= test_start:
        raise ValueError("Training labels overlap the test feature period.")
    return train, test


def directional_accuracy(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.sign(actual) == np.sign(predicted)))


def run_experiment(dataset_path: Path) -> ExperimentResult:
    started = time.perf_counter()
    market_data = load_frozen_market_data(dataset_path)
    supervised = build_supervised_dataset(market_data)
    split_index = int(len(supervised) * TRAIN_FRACTION)
    train, test = time_ordered_split(supervised)

    x_train = train.loc[:, FEATURE_COLUMNS]
    y_train = train["target_return_21d"]
    x_test = test.loc[:, FEATURE_COLUMNS]
    y_test = test["target_return_21d"]

    baseline_value = float(y_train.mean())
    baseline_predictions = np.full(len(y_test), baseline_value)

    model = _gradient_boosting_model()
    model.fit(x_train, y_train)
    model_predictions = model.predict(x_test)

    runtime_seconds = time.perf_counter() - started
    actual = y_test.to_numpy()

    result = ExperimentResult(
        dataset_path=dataset_path.as_posix(),
        dataset_sha256=file_sha256(dataset_path),
        raw_rows=len(market_data),
        usable_rows=len(supervised),
        candidate_train_rows=split_index,
        purged_train_rows=split_index - len(train),
        train_rows=len(train),
        test_rows=len(test),
        train_start=train["Date"].min().date().isoformat(),
        train_end=train["Date"].max().date().isoformat(),
        train_target_end=train["target_date"].max().date().isoformat(),
        test_start=test["Date"].min().date().isoformat(),
        test_end=test["Date"].max().date().isoformat(),
        forecast_horizon_trading_days=FORECAST_HORIZON_DAYS,
        baseline_description="Constant prediction equal to the training-set mean 21-day return",
        baseline_mae=float(mean_absolute_error(actual, baseline_predictions)),
        baseline_rmse=float(math.sqrt(mean_squared_error(actual, baseline_predictions))),
        baseline_directional_accuracy=directional_accuracy(actual, baseline_predictions),
        model_description=(
            "GradientBoostingRegressor with 100 estimators, learning_rate=0.05, "
            "max_depth=2, min_samples_leaf=8, random_state=42"
        ),
        model_mae=float(mean_absolute_error(actual, model_predictions)),
        model_rmse=float(math.sqrt(mean_squared_error(actual, model_predictions))),
        model_r2=float(r2_score(actual, model_predictions)),
        model_directional_accuracy=directional_accuracy(actual, model_predictions),
        runtime_seconds=float(runtime_seconds),
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    return result


def save_result(result: ExperimentResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
