# WaterBuddy version 2

Live app: https://waterbuddy-sharv.streamlit.app/

A Python and Streamlit hydration tracker for FA2, with a matching FA1 storyboard.

## Run in VS Code

Open the WaterBuddy folder containing app.py. In Terminal > New Terminal run:

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use Python 3.12. Open http://localhost:8501 and leave the terminal running. Live Server does not execute Python. RUN_WATERBUDDY.cmd also installs requirements and starts the app. After installation, Terminal > Run Task > Run WaterBuddy starts it. Ctrl+C stops it.

## Features

Choose an age group and adjust the goal. Add +100, +250 or +500 ml, a custom amount or a container fraction. Total, remaining water, percentage, bar and mascot update live. The mascot reacts at 50%, 75% and 100%. Undo removes the last drink; confirmed reset clears today without losing settings or earlier dates.

Plan builds check-ins using your waking hours, reminder spacing and busy-hour exclusions. Progress shows seven dated records, a session summary, CSV/JSON downloads and confirmed backup restore. Rewards shows real-date streaks, badges and capped points. About explains the goal guidance.

## Personal schedule and sound alarms

In Reminders and clock, choose your day start/end and spacing (15, 30, 60, 90, 120 or 180 minutes). Select busy hours to skip, such as lessons or work. Plan shows the available check-ins, next planned time and a flexible goal-by-time comparison. It uses your choices, not an AI health assessment. Overnight schedules are not supported. If all hours are busy there are no slots. Missed slots never count as drinks or create a catch-up drinking target.

Enable Show in-app reminders and optionally Sound alarm when due. Tap play in the audio player to test the sound. Home checks every 60 seconds. Reminders require: enabled setting, waking hours, non-busy hour, incomplete goal, elapsed interval since last log/session start and expired snooze. Sound repeats at most once per chosen interval. Logging restarts the interval; snooze hides reminders for 15 minutes.

Keep Home open and connected. Browsers can block autoplay or slow background tabs, and device volume matters. There are no closed-tab, phone, operating-system, email or push alarms. Planned slots can differ from actual reminders because logging and snoozing change the reminder clock. Test audio on the device used for the demonstration.

## Records and restore

Each visitor has a separate server-side Streamlit session. There is no account, database or automatic cross-device sync. A restart or expired session can lose data; download backups. Date rollover creates a new actual date. Reset cannot manufacture a streak.

In Progress, choose a water-record JSON backup and confirm replacement. Validation checks size, age, goals, dates and drink entries before replacing anything. Invalid files keep current data intact. Restore syncs age and goal controls while keeping current schedule preferences. A plan JSON is a separate readable export, not a water backup; schedule import is not implemented. UTC offset defaults to India (+5:30) and does not automatically follow daylight saving.

## Goal guidance

Age presets are illustrative classroom logging goals, not personalised medical advice. EFSA values include food and all drinks; see About for the distinction. Children should choose a suitable goal with an adult. Individual clinical advice and fluid restrictions take priority. Extra water above the goal earns no additional rewards. Goal changes, undo and reset recalculate points.

## Files and verification

app.py contains the interface, callbacks, SVG mascot and generated WAV alarm. hydration.py holds calculations and calendar rewards. planning.py holds scheduling, reminder eligibility and backup validation. requirements.txt pins Streamlit 1.66.0. Other imports are standard Python modules. .streamlit/config.toml defines the theme.

```text
python -m unittest -v test_waterbuddy.py test_planning.py
python test_interface.py
```

Version 2 passed 19 pure logic tests and 23 Streamlit AppTest checkpoints locally on 2 November 2026. See TEST_RESULTS.txt. Sound delivery still depends on browser/device settings.

## Deployment and submission

GitHub main is linked to Streamlit Cloud using app.py and Python 3.12. Deploy app.py, hydration.py, planning.py, requirements.txt and .streamlit/config.toml together. No secrets are required. Use the revised storyboard supplied with this version. The submission links PDF contains the app and hosted-storyboard links; until the revised PDF is uploaded, the hosted storyboard can show the previous version.

## References

- https://www.efsa.europa.eu/sites/default/files/2017_09_DRVs_summary_report.pdf
- https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
