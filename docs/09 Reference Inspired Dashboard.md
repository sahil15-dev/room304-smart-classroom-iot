# Room 304 — Reference-Inspired Dashboard Update

This upgrade adapts the layout and workflow of the reference dashboard that you supplied to the **working Room 304 Smart Classroom** project. It intentionally uses your existing real data pipeline; it does not replace the Arduino program or the Python bridge.

## Differences from the standalone reference HTML

- The reference HTML expects a standalone `data.csv` and optionally simulates measurements. The Room 304 version reads **`/api/live`** from the existing Flask backend, which reads real data from `data/logs/room304 readings.csv`.
- ThingSpeak API keys **do not appear in HTML or JavaScript**. The Flask server uses `THINGSPEAK_CHANNEL_ID` and `THINGSPEAK_READ_KEY` from your local `.env` to query the cloud and offers a key-free `/api/cloud` response.
- If the bridge is stopped, the dashboard identifies the data as **delayed/offline**, instead of showing a fake live connection. If the CSV file is absent, the page displays a waiting message, not simulated sensor values.
- Door open/closed is the **reported** reed input (magnet test pending), and classroom mode is **expected occupied/empty** selected by the physical button, not measured occupancy.
- RGB LED color is the **expected firmware indication**; confirm the actual LED/buzzer visually before marking them as tested.
- Light is **raw ADC**, lower means brighter with your specific sensor setup, not lux. Sound is a **signal span**, not decibels. PIR is intentionally **not installed** and remains disabled.

## What's added

- Sidebar navigation with **Overview**, **Test & calibrate**, **Data history**.
- An illustrative Room 304 schematic showing the UNO, button, reed switch, alert indicator and reserved PIR pin. **Not a measured or surveyed room floorplan**.
- Live sensor KPI cards with small sparklines and relative meters; one main trend chart with temperature/humidity/light/sound selector and sample-window options.
- Accurate alert labels for firmware codes 0 (normal), 1 (comfort warning), 2 (possible lighting waste) and **3 (DHT sensor fault)**.
- Local state-transition events, cloud freshness information, manual refresh and dark/light themes.
- Seven **manual** classroom test signoffs, live sensor diagnostics, snapshot capture buttons and exportable test notes. Tick items only after physically verifying the hardware.
- The **Test & calibrate checklist scrolls** on desktop, while the whole page scrolls on smaller screens.
- The **Data history table scrolls vertically and horizontally**, with a sticky header; choose the last 20, 50, 100, 200 or 480 rows. The backend returns up to 800 recent samples to support scrolling, and the **Download full CSV** button uses the original Flask download endpoint to export the entire log, not just displayed rows.

## Install into your existing VS Code + PlatformIO project

1. Save local edits and check `git status`. If you customized the existing dashboard, make a copy of those files before overwriting.
2. Stop only the website process (`python -m dashboard.app`) by pressing **Ctrl+C** in its terminal. The bridge can keep running.
3. Extract `Room304DashboardReference.zip` and copy these **four files** into matching locations in your existing `room304 smart classroom iot` folder:

   - `dashboard/templates/index.html` — redesigned website
   - `dashboard/app.py` — existing Flask API with 800-sample history capacity
   - `tests/testdashboard.py` — updated tests
   - `docs/09 Reference Inspired Dashboard.md` — this guide

4. **Do not** replace `.env`, `bridge/`, `firmware/`, `platformio.ini`, or `.git`. No other packages are required if the previous dashboard already ran successfully.
5. In the project root terminal, check the tests:

   ```powershell
   python -m unittest discover -s tests -v
   ```

6. Start or keep the **Python bridge** in Terminal 1 (PlatformIO Monitor must be closed so COM3 is free):

   ```powershell
   python -m bridge.runner
   ```

7. Run the **website** in Terminal 2:

   ```powershell
   python -m dashboard.app
   ```

8. Open `http://127.0.0.1:5000` and press **Ctrl+Shift+R** if the previous design is cached.

## Verify the changes

- **Overview:** readings match the Python bridge; selecting each metric updates the single chart; Try switching between dark and light themes.
- **Test & calibrate:** move the mouse over the checklist and scroll down to the bottom; use `Capture dark` after covering the photoresistor, then `Capture flashlight` while illuminating it. Check that the notes are updated. Export the report.
- **Data history:** select `Last 200 rows` or `Last 480 rows`, scroll the table up and down, and use the horizontal scroll when your window is narrow. Download full CSV and confirm it's real readings from your bridge.
- **ThingSpeak:** verify recent cloud points and timestamp, not just a historical nonzero count.

## Tomorrow's classroom validation

Bring your Arduino prototype, USB cable and a small magnet. Verify reed input with magnet near/far, light covered/ambient/flashlight, microphone quiet/clapping, physical mode button, blue/green/red LED indication and buzzer. Record the actual values; do not fabricate readings. PIR remains reserved for D7 and disabled until you have the module.

## Save this to your existing GitHub repository

Review the changes, then commit only the upgraded files:

```powershell
git status
git add dashboard/app.py dashboard/templates/index.html tests/testdashboard.py "docs/09 Reference Inspired Dashboard.md"
git diff --cached --check
git diff --cached --name-only
git ls-files .env
# the preceding command should produce no output
git commit -m "Adopt improved Room 304 dashboard layout and scrollable history"
git push
```

If `git ls-files .env` prints a tracked secret file, do **not** push until it is addressed. The source does not contain real ThingSpeak API keys.

## Limits

- **Monitoring-only:** The website does not control hardware outputs, door locks, lights or HVAC. Only the physical button changes the expected-empty mode.
- The dashboard reads the local CSV produced by the bridge. Keep both processes running for live monitoring. The website runs on localhost by default, not as a publicly reachable site.
- Browser notes and checkmarks are browser-local. Use **Export test report** to preserve your work.
- Local history is limited to the most recent 800 samples in the API to avoid unbounded page loads. Full CSV download includes the whole local file.
- This package was checked with a browser using fixture data. The actual COM3 and ThingSpeak setup must be verified on your Windows laptop.
