import json
import math
from pathlib import Path
from unittest import TestCase

from ai_feasibility.experiment import (
    FEATURE_COLUMNS,
    build_supervised_dataset,
    file_sha256,
    load_frozen_market_data,
    run_experiment,
    time_ordered_split,
)


DATASET = Path(__file__).resolve().parents[1] / "data" / "aapl_daily_2015_2017.csv"
RECORDED_RESULTS = (
    Path(__file__).resolve().parents[1] / "artifacts" / "ai_feasibility_results.json"
)


class AIFeasibilityTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.market_data = load_frozen_market_data(DATASET)
        cls.supervised = build_supervised_dataset(cls.market_data)

    def test_frozen_dataset_has_expected_boundaries(self):
        self.assertEqual(len(self.market_data), 506)
        self.assertEqual(self.market_data["Date"].min().date().isoformat(), "2015-02-17")
        self.assertEqual(self.market_data["Date"].max().date().isoformat(), "2017-02-16")
        self.assertFalse(self.market_data["Date"].duplicated().any())
        self.assertEqual(
            file_sha256(DATASET),
            "04053fd4ab339dd81a2bd14153e4be4fd88ae209fbc7aca29bc1096a3cbe7f27",
        )

    def test_features_and_target_are_complete(self):
        required = [*FEATURE_COLUMNS, "target_return_21d", "target_date"]
        self.assertFalse(self.supervised[required].isna().any().any())
        self.assertGreaterEqual(len(self.supervised), 100)

    def test_target_is_the_forward_21_trading_day_return(self):
        row = self.supervised.iloc[0]
        current = self.market_data.loc[
            self.market_data["Date"] == row["Date"], "adjusted_close"
        ].iloc[0]
        future = self.market_data.loc[
            self.market_data["Date"] == row["target_date"], "adjusted_close"
        ].iloc[0]
        self.assertAlmostEqual(row["target_return_21d"], future / current - 1)

    def test_features_do_not_use_future_values(self):
        feature_date = self.supervised.iloc[0]["Date"]
        changed_market_data = self.market_data.copy()
        feature_index = changed_market_data.index[
            changed_market_data["Date"] == feature_date
        ][0]
        changed_market_data.loc[feature_index + 1, "adjusted_close"] *= 10
        changed = build_supervised_dataset(changed_market_data)

        original_features = self.supervised.loc[
            self.supervised["Date"] == feature_date, FEATURE_COLUMNS
        ].iloc[0]
        changed_features = changed.loc[
            changed["Date"] == feature_date, FEATURE_COLUMNS
        ].iloc[0]
        self.assertTrue(original_features.equals(changed_features))

    def test_split_is_strictly_time_ordered(self):
        train, test = time_ordered_split(self.supervised)
        self.assertLess(train["Date"].max(), test["Date"].min())
        self.assertLess(train["target_date"].max(), test["Date"].min())
        self.assertEqual(len(self.supervised) - len(train) - len(test), 21)

    def test_experiment_produces_finite_real_metrics(self):
        result = run_experiment(DATASET)
        self.assertEqual(result.purged_train_rows, 21)
        self.assertEqual(result.candidate_train_rows, 348)
        self.assertEqual(
            result.train_rows + result.test_rows + result.purged_train_rows,
            result.usable_rows,
        )
        for metric in (
            result.baseline_mae,
            result.baseline_rmse,
            result.baseline_directional_accuracy,
            result.model_mae,
            result.model_rmse,
            result.model_r2,
            result.model_directional_accuracy,
            result.runtime_seconds,
        ):
            self.assertTrue(math.isfinite(metric))
        self.assertGreater(result.runtime_seconds, 0)

    def test_model_metrics_are_deterministic(self):
        first = run_experiment(DATASET)
        second = run_experiment(DATASET)
        self.assertEqual(first.dataset_sha256, second.dataset_sha256)
        self.assertEqual(first.model_mae, second.model_mae)
        self.assertEqual(first.model_rmse, second.model_rmse)
        self.assertEqual(
            first.model_directional_accuracy,
            second.model_directional_accuracy,
        )

    def test_recorded_results_match_a_fresh_execution(self):
        recorded = json.loads(RECORDED_RESULTS.read_text(encoding="utf-8"))
        fresh = run_experiment(DATASET).to_dict()
        stable_fields = (
            "dataset_sha256",
            "raw_rows",
            "usable_rows",
            "candidate_train_rows",
            "purged_train_rows",
            "train_rows",
            "test_rows",
            "train_start",
            "train_end",
            "train_target_end",
            "test_start",
            "test_end",
            "baseline_mae",
            "baseline_rmse",
            "baseline_directional_accuracy",
            "model_mae",
            "model_rmse",
            "model_r2",
            "model_directional_accuracy",
        )
        for field in stable_fields:
            self.assertEqual(recorded[field], fresh[field], field)
