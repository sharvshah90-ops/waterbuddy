# WaterBuddy

A modular Python and Streamlit hydration companion for FA2. The matching revised FA1 storyboard describes this implementation.

## Run locally

Install Python 3.12, open a terminal in this folder, then run:

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows you can also double-click `RUN_WATERBUDDY.cmd` after installing Python. The launcher installs the pinned requirements and starts the app. It needs internet for the first installation.

## Features

### Run in VS Code

Open this WaterBuddy folder (the one containing app.py) in VS Code. Open Terminal > New Terminal and run the two commands above. Keep the terminal running and open http://localhost:8501. Live Server does not execute Python. After installing requirements once, you can also use Terminal > Run Task > Run WaterBuddy. Press Ctrl+C in the terminal to stop the app.

- Four age groups with editable, clearly labelled classroom goal presets.
- +250 ml, custom amounts, saved glass and bottle sizes, and fractions.
- Live total, non-negative remaining amount, true percentage and capped progress bar.
- Original Python-drawn drop mascot with reactions at 50%, 75% and 100%.
- Undo and confirmed reset that keep settings and earlier calendar dates.
- Points capped at 125 per day, badges and cosmetic celebration choices.
- Real calendar streaks, seven-day records, drink log, CSV and JSON downloads.
- Optional in-app reminders with quiet hours and 15-minute snooze.
- No login or database. Each user's Streamlit session is separate.

## Important behavior

The app uses server-side session memory. Reloading/reconnecting may lose the session, and a server restart loses it. History and streaks refer only to dates still in that session; there is no permanent cross-device history. Download CSV or JSON for a personal record. JSON import is not implemented.

The app checks the local date on interaction and every 60 seconds while Home is open. A new actual date starts a new record. The Reset button clears the current date; it cannot be used to manufacture a streak. The UTC offset defaults to India (+5:30), and can be changed in settings. This fixed offset does not automatically follow daylight saving.

Reminders appear on Home only while the app is open and connected. There are no background, browser, email or desktop push notifications. The timer starts when a new session starts or water is logged, and pauses display during 22:00-07:00 local quiet hours. Reminders stop at goal completion.

Age presets are illustrative starting goals from the project concept, not medical prescriptions. EFSA reference values concern total water from food and all drinks. The About section explains this distinction and links to primary sources. No additional rewards are earned by exceeding the goal. Points and badges recalculate when logs or the goal change.

## Files

`app.py` contains the web interface and callbacks. `hydration.py` contains independently testable calculations, date records and reward rules. `requirements.txt` pins Streamlit. `.streamlit/config.toml` defines the theme. The SVG mascot is created in Python, so no desktop Tkinter or Turtle dependency is needed in the cloud.

## Verify

```text
python -m unittest -v test_waterbuddy.py
python test_interface.py
```

The first command checks 11 groups of logic and boundary cases. The second uses Streamlit's AppTest to check the interface. Check `TEST_RESULTS.txt` for the recorded run. These checks do not prove a public deployment works.

## Deploy on Streamlit Community Cloud

1. Sign in to GitHub and create a public repository named `waterbuddy`. Do not upload personal water records, credentials, the dependency download folder, or temporary files.
2. Upload `app.py`, `hydration.py`, `requirements.txt`, `README.md`, and `.streamlit/config.toml`. Keep these files at the repository root and the config inside `.streamlit`. The two test files are optional for deployment.
3. At https://share.streamlit.io, sign in with GitHub. Choose **Create app**, then **Yup, I have an app**. Select the repository, its actual branch (usually `main`), and `app.py` as the entrypoint.
4. In Advanced settings choose Python 3.12. No secrets, database or API keys are required. Deploy and wait for the build.
5. Open the generated `https://...streamlit.app` address in a signed-out/private browser and test age selection, +250 ml, milestones and reset. Fix any deployment error before submitting.
6. Upload `WaterBuddy_FA1_Storyboard.pdf` to a teacher-accessible location, such as your school OneDrive or Google Drive. Set viewer access appropriate for your teacher and verify the link from a separate browser session.
7. Open `SUBMISSION_LINKS.html` from the complete pack, paste both verified links, and print/save it as PDF. Submit that PDF as the brief requests. The local app address is not a deployed-project link.

**Current status:** Source and local testing are complete. Public deployment and a hosted storyboard link are pending because GitHub was signed out in the available browser. No public URL is claimed.

## Explain the code in your demonstration

Start with the pure functions in `hydration.py`. Show how a button callback adds a drink to `st.session_state.model`. Explain why `remaining` is clamped at zero while the numerical percentage can exceed 100%, and why the progress bar is capped at 1.0. Demonstrate Cancel versus Confirm on reset. Explain session memory and the difference between a calendar rollover and manual reset. Review the code and be able to explain it before presenting.

## Sources

- EFSA dietary reference values: https://www.efsa.europa.eu/sites/default/files/2017_09_DRVs_summary_report.pdf
- CDC water guidance: https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/
- Streamlit deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit dependency management: https://docs.streamlit.io/deploy/concepts/dependencies
