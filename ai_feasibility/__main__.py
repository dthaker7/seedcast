import argparse
import json
from pathlib import Path

from .experiment import run_experiment, save_result


DEFAULT_DATASET = Path("data/aapl_daily_2015_2017.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Seedcast's frozen-data AI feasibility experiment."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"Frozen OHLCV CSV (default: {DEFAULT_DATASET.as_posix()})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON path for recording this execution's results.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_experiment(args.data)
    if args.output:
        save_result(result, args.output)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
