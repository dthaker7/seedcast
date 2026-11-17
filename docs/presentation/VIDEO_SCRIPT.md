# Seedcast four-minute product demo

Target length: 3:50-4:00. Record the browser at 1440 x 900 or larger. Keep the terminal ready in a second window.

## 0:00-0:20 - Product introduction

**Screen:** Seedcast landing page.

**Narration:**

"Seedcast is an educational finance application for students, recent graduates, and other beginning investors. It starts with the money someone actually has available, then connects that plan to understandable market forecasts. Seedcast uses paper-money simulations and does not provide investment advice."

## 0:20-0:50 - Problem and solution

**Screen:** Move from the landing page to the signup or dashboard page.

**Narration:**

"A beginner may have a small monthly surplus but no clear way to decide whether to strengthen savings, pay extra debt, or practice investing. Budget tools and market screeners usually separate those decisions. Seedcast combines a personal money snapshot, a transparent Seed Split, and uncertainty-aware market information in one workflow."

## 0:50-1:45 - Complete money workflow

**Actions:** Sign in. Open the profile form. Show emergency-fund months and risk comfort. Submit a monthly snapshot with valid income and expenses. Show the dashboard result.

**Narration:**

"The user first saves a financial profile. I will enter the monthly snapshot and submit it. Django validates the input, stores it under the signed-in user, and calculates the monthly surplus. The dashboard then divides a positive surplus into three initial buckets: emergency savings, extra debt payoff when debt exists, and paper-money practice. The rules and explanations remain visible, and automated tests confirm that one user cannot access another user's financial records."

## 1:45-2:15 - Markets Explorer

**Actions:** Open Cast Explorer. Search for AAPL. Clear the search. Filter by individual stock. Open AAPL.

**Narration:**

"Cast Explorer provides a curated market universe with search and asset-type filtering. The application reads cached prices instead of calling a live market API during a page request. Opening Apple shows the latest saved price, the model forecast, its range, and the date. Because the frozen demonstration data ends in 2017, Seedcast labels the result stale instead of presenting it as current advice."

## 2:15-2:50 - Working AI integration

**Actions:** Show a terminal and run `python manage.py load_demo_market_data`. Return to AAPL and refresh. Briefly open `/markets/api/forecasts/AAPL/`.

**Narration:**

"This command demonstrates the complete AI path. It loads 506 frozen Apple price observations, constructs momentum, volatility, moving-average, and volume features, then trains scikit-learn gradient-boosting models offline. The command saves a real Forecast record through Django. The page and JSON API read that saved record. Normal web requests never retrain the model while a user waits."

## 2:50-3:30 - Technical implementation

**Screen:** Poster architecture diagram or repository files, then return to the application.

**Narration:**

"Seedcast uses Django templates, forms, authentication, SQLite, internal JSON endpoints, pandas, NumPy, and scikit-learn. FinancialProfile has a one-to-many relationship with monthly budgets. MarketAsset owns cached PriceBar and Forecast records. The AI evaluation uses a chronological split and purges training labels that overlap the test period, which prevents look-ahead leakage. The merged project currently passes 53 automated tests."

## 3:30-3:50 - Challenge and improvement

**Screen:** Evaluation chart on the poster.

**Narration:**

"The main challenge is predictive reliability. Gradient boosting improved directional accuracy from 27.27 percent to 40.91 percent, but its MAE and RMSE were worse than the simple baseline. Our next improvement is walk-forward evaluation across more assets, followed by calibrated uncertainty and fresher licensed data."

## 3:50-4:00 - Conclusion

**Screen:** Dashboard or AAPL forecast page.

**Narration:**

"Seedcast now connects a real financial workflow to a reproducible Django and AI pipeline while communicating uncertainty and limitations honestly."

