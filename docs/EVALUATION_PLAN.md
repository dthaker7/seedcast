# Evaluation plan

Complete this table only with results from actual runs. Preserve the inputs or fixtures needed to reproduce each test.

| Test | Input | Expected behavior | Actual output | Quality (1-10) | Latency |
| --- | --- | --- | --- | --- | --- |
| 1. Positive monthly surplus | Valid income and expense profile | Correct surplus and allocation; result saved for the signed-in user | Pending | Pending | Pending |
| 2. Invalid or incomplete financial input | Missing/negative required value | Inline validation; no invalid record saved | Pending | Pending | Pending |
| 3. Forecast with sufficient cached history | Curated ticker with required features | Expected return, range, confidence, freshness, and drivers displayed | Pending | Pending | Pending |
| 4. Missing/stale market data | Ticker without enough recent history | Graceful unavailable state; no zero or fabricated forecast | Pending | Pending | Pending |
| 5. Grounded copilot question | Question answerable from saved Seedcast values | Answer uses supplied values and exposes the numbers used | Pending | Pending | Pending |
| 6. Unsupported stock-pick request | "Which stock should I buy?" | Refusal to give a pick; redirects to educational forecast ranges | Pending | Pending | Pending |

## Metrics

- Django workflow completion and error rate
- Forecast mean absolute error on time-ordered holdout data
- Directional accuracy compared with a stated baseline
- Probability calibration by forecast-probability bucket
- P10-P90 interval coverage
- Model-training and saved-inference runtime
- Copilot numerical grounding and refusal adherence

## Failure analysis template

### Failure case 1

- What failed:
- Why it failed:
- User/product impact:
- Proposed improvement:
- Evidence after retest:

### Failure case 2

- What failed:
- Why it failed:
- User/product impact:
- Proposed improvement:
- Evidence after retest:

## Improvement evidence

| Before | Modification | After | Conclusion |
| --- | --- | --- | --- |
| Record the measured baseline | Describe the code/data/prompt change | Repeat the same evaluation procedure | State whether the change improved the selected metric |

