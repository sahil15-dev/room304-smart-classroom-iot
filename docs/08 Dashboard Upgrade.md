# Room 304 — Dashboard Upgrade

This update is an **add-on for the existing Room 304 GitHub project**, not a replacement for the Arduino firmware or Python bridge. It uses the same local CSV and ThingSpeak feed. It remains **read-only**: use the physical button to change the Arduino's expected-empty mode.

## What changed

- Cleaner and more consistent responsive desktop/mobile layout, retaining the dark palette.
- **One selectable chart**: temperature, humidity, raw light ADC or relative sound span. Choose 40, 120 or 300 recent samples.
- **Recent events** generated from changes recorded in the local CSV: Arduino mode, reed input and firmware alert code. Events are observations, not proof of physical occupancy or a calibrated door state.
- **Test & calibrate** page: seven manual verification checkboxes and classroom notes. These are saved in *this browser's local storage*; export the text report before clearing browser data or moving to a classroom computer.
- **Data history** page: last 20 local readings plus an actual download of the entire CSV (`/api/export.csv`).
- ThingSpeak status with recent point count and a manual refresh button. Private API keys stay in `.env` and are never sent to the browser.

## Install safely in your existing VS Code project

1. Keep both working terminals if running, but press `Ctrl+C` in the `python -m dashboard.app` terminal. **Do not stop your bridge unless needed.**
2. In the project root, inspect and save local changes: `git status`. If you made your own edits to the original dashboard, back up those files first.
3. Extract `Room304DashboardUpgrade.zip`. Copy **only** these into the existing project, preserving their directory structure:

   - `dashboard/app.py`
   - `dashboard/templates/index.html`
   - `tests/testdashboard.py`
   - `docs/08 Dashboard Upgrade.md`

   You do **not** need to replace `.env`, `bridge/`, `firmware/`, `requirements.txt`, `platformio.ini`, or your existing Git repository. The bundled dashboard folder contains `requirements.txt`, `Dockerfile` and `__init__.py` matching the previous website; these can stay untouched.

4. From the existing VS Code project root, run:

   ```powershell
   python -m pip install -r requirements.txt -r dashboard/requirements.txt
   python -m unittest discover -s tests -v
   python -m dashboard.app
   ```

5. Refresh **http://127.0.0.1:5000**. If the old UI is cached, press `Ctrl+Shift+R`.
6. Terminal 1, if not already running: close PlatformIO Serial Monitor, then run `python -m bridge.runner` to provide live COM3 data and ThingSpeak uploads. Terminal 2: `python -m dashboard.app`.

## Tomorrow in Room 304

- Take screenshots of the Overview and cloud status after the bridge starts receiving readings.
- Use **Test & calibrate** to check DHT, cover/flashlight LDR measurements (lower ADC = brighter), quiet/clapping sound, reed with magnet, button mode, LED/buzzer, and at least 10 ThingSpeak uploads.
- Record dark/ambient/flashlight ADC values and quiet/loud sound span in Notes. Select firmware thresholds from actual classroom values; don't invent lux or decibel measurements.
- Export the test report and local CSV. Put them in your project documentation only after removing private content and checking `git status`.
- Leave PIR off until the sensor arrives.

## Save verified updates to GitHub

```powershell
git status
git add dashboard/app.py dashboard/templates/index.html tests/testdashboard.py "docs/08 Dashboard Upgrade.md"
git diff --cached --check
git diff --cached --name-only
git ls-files .env
git commit -m "Improve Room 304 dashboard and classroom test workflow"
git push
```

`git ls-files .env` should print nothing. Never commit `.env`, API keys or logs that contain private information. Check before committing generated reports.

## Current limits

- No remote control of the Arduino or actual lights, fans or HVAC. This dashboard is **monitoring-only**.
- "Live" means the local CSV was updated in the last 20 seconds, not that a remote connection was independently verified.
- Local CSV history covers only the last 480 rows in the dashboard. CSV export includes the whole file.
- ThingSpeak can show stored data even if uploads have stopped. Check the most recent cloud timestamp.
- Door state is unverified until tested with a magnet. Expected-empty is a user-selected mode, not occupancy detection. PIR is disabled.
- No paid services or third-party chart libraries required.
