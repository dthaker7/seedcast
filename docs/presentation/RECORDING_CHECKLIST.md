# Recording checklist

## Before recording

```powershell
git pull --ff-only origin main
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py load_demo_market_data
python manage.py runserver
```

- Create one clean demonstration account and a realistic financial profile.
- Keep the monthly snapshot form ready with values that produce a positive surplus.
- Open `/markets/`, `/markets/AAPL/`, and `/markets/api/forecasts/AAPL/` in separate tabs.
- Increase browser zoom only if text is difficult to read in the recording.
- Hide notifications and unrelated tabs.
- Record at 1080p when available.

## Required evidence in the video

- Product purpose and target users.
- Input, Django processing, saved database result, and visible output.
- Money Snapshot and Seed Split.
- Cast Explorer search or filtering.
- Saved AI forecast in the AAPL detail page and JSON API.
- Brief architecture explanation.
- Honest evaluation result and one planned improvement.

## Final check

- Duration is no longer than 4:00.
- Narration is audible and the pointer does not move unnecessarily.
- No passwords, private financial information, API keys, or unrelated browser content appears.
- The uploaded video plays from beginning to end.

